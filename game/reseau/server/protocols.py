class Protocols :
    class Response :
        NICKNAME = "protocol.request_nickname"
        OPPONENT = "protocol.opponent"
        START = "protocol.start"
        WINNER = "protocol.winner"
        OPPONENT_LEFT = "protocol.opponent_left"
    
    class Request:
        NICKNAME = "protocol.send_nickname"
        LEAVE = "protocol.leave"