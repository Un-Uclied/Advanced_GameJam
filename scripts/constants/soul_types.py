SOUL_DEFAULT = "X"

# 착한거!! (안전빵)
SOUL_KIND_A = "seraph" # 빛 안에 있으면 체력 빨리 참 | 이속 감소
SOUL_KIND_B = "grace"   # 빛의 범위 증가 | 안개 좀더 투명해짐 | 대미지 다운
SOUL_KIND_C = "faith"   # 이동속도 증가 | 체력은 좀 낮음 ㅇㅇ;

# 나쁜거 !! (risky but cool)
SOUL_EVIL_A = "haste" # 관통 되는 탄환 | 빠른 탄속 | 대신 쿨타임 좀 긺                (적이 갖고 있으면 이속 증가)
SOUL_EVIL_B = "wrath" # 쿨타임 엄청 짧아짐 | 체력 떡락                              (적이 갖고 있으면 대미지 증가)
SOUL_EVIL_C = "ruin"   # 맞힐수록 대미지 증가 | 처음엔 엄청 약함 | 맞으면 대미지 리셋   (적이 갖고 있으면 체력 증가)

# 적이 갖고 있으면 바뀌는 만큼의 량
EVIL_A_SPEED_UP = 2
EVIL_B_DAMAGE_UP = 15
EVIL_C_HEALTH_UP = 25

ALL_SOUL_TYPES = (SOUL_KIND_A, SOUL_KIND_B, SOUL_KIND_C, SOUL_EVIL_A, SOUL_EVIL_B, SOUL_EVIL_C)
ALL_KIND_SOUL_TYPES = (SOUL_KIND_A, SOUL_KIND_B, SOUL_KIND_C)
ALL_EVIL_SOUL_TYPES = (SOUL_EVIL_A, SOUL_EVIL_B, SOUL_EVIL_C)