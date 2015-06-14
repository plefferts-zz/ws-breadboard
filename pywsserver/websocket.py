import asynchat
import sys, random
import array, struct
import re, hashlib, base64

class WebSocketConnection(asynchat.async_chat):
    class MessageTooBig(Exception):
        pass
    class HandshakeInProgress(Exception):
        pass

    def __init__(self, sock, addr):
        asynchat.async_chat.__init__(self, sock=sock)
        self.addr = addr
        self.sock_buffer = []
        self.input_buffer = []
        self.output_buffer = []
        self.handler = WebSocketHandshake(self)
        self.handshake_completed = False
        self.maximum_message_length = (1 << 20) - 1
        self.message_type = None
    
    def collect_incoming_data(self, data):
        self.sock_buffer.append(data)

    def found_terminator(self):
        self.handler.handle_data(b''.join(self.sock_buffer))
        self.sock_buffer = []

    def handshake_complete(self):
        self.handshake_completed = True
        self.handler = WebSocketProtocol(self)

    def handle_ws_frame(self, data, final, opcode):
        self.input_buffer.append(data)
        if final:
            if opcode == WebSocketProtocol.UTF8_OPCODE:
                self.handle_utf8_message(b''.join(self.input_buffer))
            elif opcode == WebSocketProtocol.BINARY_OPCODE:
                self.handle_binary_message(b''.join(self.input_buffer))
            self.input_buffer = []
        else:
            total_length = reduce(lambda total, x : total + len(x))
            if self.maximum_message_length < total_length + len(data):
                raise self.MessageTooBig()

    def send_binary_message(self, data):
        if not self.handshake_completed:
            raise HandshakeInProgress();
        self.handler.send_binary_frame(data)
    
    def send_utf8_message(self, data):
        if not self.handshake_completed:
            raise HandshakeInProgress();
        self.handler.send_utf8_frame(data)

    def handle_binary_message(self, data):
        raise NotImplementedError
    
    def handle_utf8_message(self, data):
        raise NotImplementedError


class WebSocketHandshake(object):

    def __init__(self, connection):
        self.connection = connection
        self.request = None
        self.handler = HTTPRequest(self)
    
    def set_terminator(self, terminator):
        self.connection.set_terminator(terminator)

    def close(self):
        self.connection.close()

    def handle_data(self, data):
        try:
            self.handler.handle_data(data)
        except HTTPRequest.BadRequestError:
            self.connection.push(b'HTTP/1.1 400 Bad Request\r\n\r\n')
            self.close()
    
    def handle_http_request(self, request):
        self.request = request
        if not self.is_supported(request['headers']):
            raise HTTPRequest.BadRequestError
        try:
            version = int(request['headers']['sec-websocket-version'])
        except ValueError:
            raise HTTPRequest.BadRequestError
        if not self.check_version(version):
            return # leave connection open for re-try
        sha1 = hashlib.sha1()
        key = request['headers']['sec-websocket-key']
        sha1.update(bytes(key, encoding='utf8'))
        magic = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        sha1.update(magic)
        digest = base64.b64encode(sha1.digest())
        response = (b'HTTP/1.1 101 Switching Protocols\r\n' +
                    b'Upgrade: websocket\r\n' +
                    b'Connection: Upgrade\r\n' +
                    b'Sec-WebSocket-Accept: ' + digest + b'\r\n'
                   )
        self.connection.push(response + b'\r\n')
        self.connection.handshake_complete()
    
    def check_version(self, version):
        if version < 13:
            self.connection.push(
                b'HTTP/1.1 426 Upgrade Required\r\n' +
                b'Sec-WebSocket-Version: 13\r\n\r\n'
            )
            return False
        if version > 13:
            self.connection.push(
                b'HTTP/1.1 400 Bad Request\r\n' +
                b'Sec-WebSocket-Version: 13\r\n\r\n'
            )
            return False
        return True
    
    def is_supported(self, headers):
        if ('host' not in headers):
            return False
        if ('connection' not in headers
            or headers['connection'].lower() != 'upgrade'
           ):
            return False
        if ('upgrade' not in headers
            or headers['upgrade'].lower() != 'websocket'
           ):
            return False
        if ('sec-websocket-version' not in headers):
            return False
        if 'sec-websocket-key' not in headers:
            return False
        return True


class HTTPRequest(object):

    class BadRequestError(Exception):
        pass
    
    def __init__(self, connection):
        self.connection = connection
        self.reset()

    def handle_data(self, data):
        if(self.headers == None):
            try:
                self.headers = self.parse_headers(str(data, encoding='ascii'))
                if 'content-length' in self.headers:
                    length = int(self.headers['content-length'])
                    self.connection.set_terminator(length)
                    return
            except ValueError as e:
                raise self.BadRequestError()
            except Exception as e:
                raise e #self.BadRequestError()
        elif(self.data == None):
            self.data = data
        req = {
            'method'       : self.method,
            'request_uri'  : self.request_uri,
            'http_version' : self.http_version,
            'headers'      : self.headers,
            'data'         : self.data
        }
        self.reset()
        self.connection.handle_http_request(req)
    
    def reset(self):
        self.method = None
        self.request_uri = None
        self.http_version = None
        self.headers = None
        self.data = None
        #todo: DOS prevention ,,,,
        self.connection.set_terminator(b"\r\n\r\n")

    def parse_headers(self, header):
        header = header.split('\r\n')
        request_line = header.pop(0).split(' ')
        self.method, self.request_uri, self.http_version = request_line
        headers = {}
        previous_key = None
        for line in header:
            if previous_key != None and line[0] in ' \r\n\t':
                headers[previous_key.lower()] += ' ' + line.lstrip(' \r\n\t')
            else:
                key, sep, value = line.partition(':')
                headers[key.lower()] = value.lstrip(' \r\n\t')
                previous_key = key
        return headers

class WebSocketProtocol(object):
    
    class UnexpectedOpcodeError(Exception):
        pass

    class FragmentedControlFrameError(Exception):
        pass
    
    CONTINUATION_OPCODE = 0
    UTF8_OPCODE         = 1
    BINARY_OPCODE       = 2
    CLOSE_OPCODE        = 8
    PING_OPCODE         = 9
    PONG_OPCODE         = 10
    
    valid_opcodes = [
        CONTINUATION_OPCODE,
        UTF8_OPCODE,
        BINARY_OPCODE,
        CLOSE_OPCODE,
        PING_OPCODE,
        PONG_OPCODE
    ]
    
    NORMAL_CLOSURE            = 1000
    GOING_AWAY_CLOSURE        = 1001
    PROTOCOL_ERROR_CLOSURE    = 1002
    UNACCEPTABLE_DATA_CLOSURE = 1003
    INCOSISTENT_DATA_CLOSURE  = 1007
    VIOLATED_POLICY_CLOSURE   = 1008
    MESSAGE_TOO_BIG_CLOSURE   = 1009
    EXTENSION_ERROR_CLOSURE   = 1010
    UNEXPECTED_ERROR_CLOSURE  = 1011

    def __init__(self, connection):
        self.connection = connection
        self.request = None
        self.current_opcode = None
        self.handler = WebSocketFrame(self)
    
    def set_terminator(self, terminator):
        self.connection.set_terminator(terminator)
    
    def close(self):
        self.connection.close()

    def handle_data(self, data):
        try:
            self.handler.handle_data(data)
        except WebSocketFrame.FrameExceedsMaximumSizeError:
            frame = self.close_frame(self.MESSAGE_TOO_BIG_CLOSURE)
            self.connection.push(frame)
            self.close()
        except (WebSocketFrame.UnmaskedFrameError, 
                WebSocketFrame.UnknownOpcodeError,
                WebSocketFrame.NonNegotiatedExtensionsError
               ):
            frame = self.close_frame(self.PROTOCOL_ERROR_CLOSURE)
            self.connection.push(frame)
            self.close()
    
    def handle_ws_frame(self, opcode, payload, final):

        if opcode & 8:
            if not final:
                raise FragmentedControlFrameError()
            if opcode == self.CLOSE_OPCODE:
                if len(payload) >= 2:
                    reason = struct.unpack('!H', payload)[0]
                else:
                    reason = self.NORMAL_CLOSURE
                self.connection.push(self.close_frame(reason))
                self.close()
            elif opcode == self.PING_OPCODE:
                self.connection.push(self.pong_frame(payload))
            elif opcode == self.PONG_OPCODE:
                pass
            else:
                raise WebSocketFrame.UnknownOpcodeError
        else:
            if self.current_opcode == None:
                if opcode == self.CONTINUATION_OPCODE:
                    raise UnexpectedOpcodeError()
                self.current_opcode = opcode
            else:
                if opcode != self.CONTINUATION_OPCODE:
                    raise UnexpectedOpcodeError()
            self.connection.handle_ws_frame(payload, final, self.current_opcode)
            if final:
                self.current_opcode = None

            
    def frame_length(self, length):
        if length <= 125:
            return bytes([length])
        if length < 65536:
            return bytes([126]) + struct.pack('!H', length)
        return bytes([127]) + struct.pack('!Q', length)
    
    def close_frame(self, code, message=b''):
        msg = bytes([
            WebSocketFrame.BIT_1 | self.CLOSE_OPCODE
        ])
        msg += self.frame_length(2 + len(message))
        msg += struct.pack('!H', code)
        msg += message
        return msg

    def ping_frame(self, message=b''):
        msg = bytes([
            WebSocketFrame.BIT_1 | self.PING_OPCODE
        ])
        msg += self.frame_length(len(message))
        msg += message
        return msg

    def pong_frame(self, message=b''):
        msg = bytes([
            WebSocketFrame.BIT_1 | self.PONG_OPCODE
        ])
        msg += self.frame_length(len(message))
        msg += message
        return msg

    def send_utf8_frame(self, message=b''):
        self.connection.send(self.utf8_frame(message))
        
    def utf8_frame(self, message=b''):
        msg = bytes([
            WebSocketFrame.BIT_1 | self.UTF8_OPCODE
        ])
        msg += self.frame_length(len(message))
        msg += message
        return msg

    def send_binary_frame(self, message=b''):
        self.connection.send(self.binary_frame(message))
        
    def binary_frame(self, message=b''):
        msg = bytes([
            WebSocketFrame.BIT_1 | self.BINARY_OPCODE
        ])
        msg += self.frame_length(len(message))
        msg += message
        return msg

class WebSocketFrame(object):

    class FrameExceedsMaximumSizeError(Exception):
        pass
    class NonNegotiatedExtensionsError(Exception):
        pass
    class UnmaskedFrameError(Exception):
        pass
    class UnknownOpcodeError(Exception):
        pass
    
    BIT_1               = 1 << 7
    BITS_2_TO_4         = 7 << 4
    BITS_4_TO_8         = 15
    BITS_2_TO_8         = 127
    
    def __init__(self, connection, **args):
        self.connection = connection
        if 'max_frame_length' in args:
            self.max_frame_length = args['max_frame_length']
        else: 
            self.max_frame_length = 2048
        self.reset()
    
    def reset(self):
        self.final          = None
        self.opcode         = None
        self.mask           = None
        self.payload_length = None
        self.mask_key       = None
        self.payload        = None
        self.connection.set_terminator(2)
    
    def handle_data(self, data):
        if len(data) == 0:
            return
        if self.final == None:
            self.final = True if data[0] & self.BIT_1 > 0 else False
            if data[0] & self.BITS_2_TO_4 > 0:
                bits = (data[0] & self.BITS_2_TO_4) >> 4
                msg ='Non-negotiated extensions: ' + str(bits)
                raise self.NonNegotiatedExtensionsError(msg)
            self.opcode         = data[0] & self.BITS_4_TO_8
            if self.opcode not in self.connection.valid_opcodes:
                raise self.UnknownOpcodeError()
            self.mask = True if data[1] & self.BIT_1 > 0 else False
            if not self.mask:
                raise self.UnmaskedFrameError()
            payload_length = data[1] & self.BITS_2_TO_8
            if payload_length <= 125:
                self.payload_length = payload_length
                if self.mask:
                    self.connection.set_terminator(4)
                else:
                    self.connection.set_terminator(self.payload_length)
            elif payload_length == 126:
                self.connection.set_terminator(2)
            else:
                self.connection.set_terminator(8)
        elif self.payload_length == None:
            if len(data) == 2:
                self.payload_length = struct.unpack('!H', data)[0]
            else:
                self.payload_length = struct.unpack('!Q', data)[0]
            if self.payload_length > self.max_frame_length:
                raise self.FrameExceedsMaximumSizeError(self.payload_length)
            if self.mask:
                self.connection.set_terminator(4)
            else:
                self.connection.set_terminator(self.payload_length)
        elif self.mask and self.mask_key == None:
            self.mask_key = data
            self.connection.set_terminator(self.payload_length)
        else:
            if self.mask:
                data = self.unmask(data, self.mask_key)
            self.payload = data
        
        if (self.payload_length == 0 
                and (
                    not self.mask 
                    or self.mask_key != None
                )
           ):
            self.payload = b''
        
        if self.payload != None:
            self.connection.handle_ws_frame(
                self.opcode,
                self.payload,
                self.final
            )
            self.reset()

    def unmask(self, data, mask):
        data = bytearray(data)
        for i in range(len(data)):
            data[i] = data[i] ^ mask[i % 4]
        return data
