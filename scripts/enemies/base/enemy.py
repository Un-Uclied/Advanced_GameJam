class Enemy:
    all_enemies = []
    
    #없으면 허전해서 ㅇㅇ;;
    @classmethod
    def destroy_all(cls):
        for enemy in cls.all_enemies:
            enemy.destroy_all()