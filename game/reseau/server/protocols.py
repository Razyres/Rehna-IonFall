class Protocols:
    class Response:
        NICKNAME        = "protocol.request_nickname"
        OPPONENT        = "protocol.opponent"
        START           = "protocol.start"
        WINNER          = "protocol.winner"
        OPPONENT_LEFT   = "protocol.opponent_left"
        # --- multijoueur ---
        PLAYER_ID           = "protocol.player_id"           # 1 (blue) ou 2 (red)
        OPPONENT_UPDATE     = "protocol.opponent_update"     # position adversaire
        OPPONENT_PROJECTILE = "protocol.opponent_projectile" # projectile tiré par l'adversaire
        NEXUS_DAMAGE        = "protocol.nexus_damage"        # un nexus a été touché

    class Request:
        NICKNAME        = "protocol.send_nickname"
        LEAVE           = "protocol.leave"
        # --- multijoueur ---
        PLAYER_UPDATE   = "protocol.player_update"    # envoyer sa propre position
        PROJECTILE_FIRED = "protocol.projectile_fired" # informer d'un tir
        NEXUS_HIT       = "protocol.nexus_hit"        # informer d'un dégât sur nexus
