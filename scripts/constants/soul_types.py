SOUL_DEFAULT = "X"

# 착한거!! (안전빵)
SOUL_KIND_A = "Pura"   # 빛 안에 있으면 체력 빨리 참 | 이속 감소
SOUL_KIND_B = "Solin"   # 안개 좀더 투명해짐 | 플레이어가 주는 대미지 감소
SOUL_KIND_C = "Valor"   # 이동속도 증가 | 체력은 좀 낮음 ㅇㅇ;

KIND_A_HEALTH_UP = 4
KIND_A_SPEED_DOWN = 1.2

KIND_B_FOG_ALPHA_DOWN = 150
KIND_B_ATTACK_DAMAGE_DOWN = 5

KIND_C_SPEED_UP = 1.8
KIND_C_MAX_HEALTH_DOWN = 20

# 나쁜거 !! (risky but cool)
SOUL_EVIL_A = "Ruin"   # 관통 되는 탄환 | 빠른 탄속 | 대신 쿨타임 좀 긺 | 플레이어가 공격했을때 넉백 증가 (적이 갖고 있으면 이속 증가)
SOUL_EVIL_B = "Vex"   # 쿨타임 엄청 짧아짐 | 체력 떡락                              (적이 갖고 있으면 대미지 증가)
SOUL_EVIL_C = "Morix"   # 트리플 점프 가능 | 대미지 나락 (적이 갖고 있으면 체력 증가)

EVIL_A_NUCK_BACK_UP = 1200
EVIL_A_COOLTIME_UP = .35
EVIL_A_PROJECTILE_SPEED_UP = 500

EVIL_B_COOLTIME_DOWN = .65
EVIL_B_MAX_HEALTH_DOWN = 40

SOUL_DESCRIPTION = {
    SOUL_DEFAULT : "-",

    SOUL_KIND_A : f"빛 안에 있으면 체력 회복량 증가 (+{KIND_A_HEALTH_UP})\n이동속도 감소 (-{KIND_A_SPEED_DOWN})",
    SOUL_KIND_B : f"시야 증가\n공격력 감소 (-{KIND_B_ATTACK_DAMAGE_DOWN})",
    SOUL_KIND_C : f"이동속도 증가 (+{KIND_C_SPEED_UP})\n최대체력 감소 (-{KIND_C_MAX_HEALTH_DOWN})",

    SOUL_EVIL_A : f"탄환 관통\n탄속 증가 (+{EVIL_A_PROJECTILE_SPEED_UP})\n공격속도 감소 (-{EVIL_A_COOLTIME_UP})\n공격시 넉백 증가",
    SOUL_EVIL_B : f"공격속도 증가 (+{EVIL_B_COOLTIME_DOWN})\n최대체력 감소 (-{EVIL_B_MAX_HEALTH_DOWN})",
    SOUL_EVIL_C : f"트리플 점프 가능\n시야 감소",
}

# 적이 갖고 있으면 바뀌는 만큼의 량
ENEMY_EVIL_A_SPEED_UP = 1
ENEMY_EVIL_B_DAMAGE_UP = 10
ENEMY_EVIL_C_HEALTH_UP = 25

ALL_SOUL_TYPES = (SOUL_KIND_A, SOUL_KIND_B, SOUL_KIND_C, SOUL_EVIL_A, SOUL_EVIL_B, SOUL_EVIL_C)
ALL_KIND_SOUL_TYPES = (SOUL_KIND_A, SOUL_KIND_B, SOUL_KIND_C)
ALL_EVIL_SOUL_TYPES = (SOUL_EVIL_A, SOUL_EVIL_B, SOUL_EVIL_C)