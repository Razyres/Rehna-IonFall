class Protocols :
    class Response :
        NICKNAME = "protocol.request_nickname"
        OPPONENT = "protocol.opponent"
        START = "protocol.start"
        WINNER = "protocol.winner"
        OPPONENT_LEFT = "protocol.opponent_left"
        POSITION = "protocol.request_position"
        OPP_POSITION = "protocol.opp_position"
    
    class Request:
        POSITION = "protocol.send_position"
        NICKNAME = "protocol.send_nickname"
        LEAVE = "protocol.leave"
