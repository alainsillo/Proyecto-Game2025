def draw_ui(screen, font, score, rings_collected, hearts_collected=0, power_active=False, power_timer=0, power_duration=900):
    text = font.render(f"Metros: {score} m", True, (255, 255, 255))
    screen.blit(text, (10, 10))
    
    ring_text = font.render(f"Anillos: {rings_collected} ", True, (255, 215, 0))
    screen.blit(ring_text, (10, 40))
    
    # Mostrar corazones recolectados
    heart_text = font.render(f"Corazones: {hearts_collected}/5", True, (255, 105, 180))
    screen.blit(heart_text, (10, 70))
    
    # Mostrar poder especial si está activo
    if power_active:
        # Calcular segundos restantes
        seconds_remaining = max(0, (power_duration - power_timer) // 60)
        power_text = font.render(f"⭐ THANK U NEXT! ({seconds_remaining}s)", True, (255, 215, 0))
        screen.blit(power_text, (400 - 150, 20))
    
