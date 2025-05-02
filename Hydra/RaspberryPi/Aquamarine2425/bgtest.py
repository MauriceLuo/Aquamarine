import pygame
import os
import sys

def main():
    try:
        # 初始化配置
        pygame.init()
        pygame.display.set_caption("Sensor Monitor")
        
        # 检查初始化结果
        init_result = pygame.init()
        print(f"Pygame initialized modules: {init_result}")

        # 设置窗口位置
        os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"
        
        # 创建窗口
        WIDTH, HEIGHT = 800, 600
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

        # 加载带错误处理的背景
        try:
            bg = pygame.image.load("rovbg.jpg").convert()
        except pygame.error as e:
            print(f"图片加载失败: {e}")
            bg = pygame.Surface((WIDTH, HEIGHT))
            bg.fill((30, 30, 30))  # 创建灰色背景作为fallback

        # 主循环
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # 绘制背景
            screen.blit(bg, (0,0))
            pygame.display.flip()
            clock.tick(60)

    except Exception as e:
        print(f"程序崩溃: {str(e)}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
    sys.exit()