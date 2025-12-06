# 7 RINGS RUN
Endless runner 2D hecho en **Pygame**. Controlas a Ariana, esquivas obstáculos, recolectas anillos (monedas) y corazones, activas el poder especial y compras/seleccionas skins.
<img width="1024" height="680" alt="LOGO_7RINGS_RUN" src="https://github.com/user-attachments/assets/984d1189-8437-4cad-9329-51366ba90751" />

## Requisitos
- Python 3.10+ (recomendado)
- `pip install pygame`

## Cómo descargar y ejecutar
1. Clona o descarga el repo:
	```bash
	git clone https://github.com/alainsillo/Proyecto-Game2025.git
	cd "7 Rings Run - Game"
	```
2. Instala dependencias:
	```bash
	pip install pygame
	```
3. Ejecuta el juego:
	```bash
	python main_7ringsrun.py
	```

## Controles y flujo
- `ESPACIO`: saltar/volar (mantén para propulsión).  
- `R`: reiniciar en Game Over.  
- `ESC`: volver del Shop al Menú.  
- `1-4` en la tienda: comprar/seleccionar skins (las 3-4 son “Próximamente”).

Estados del juego:
```
MENÚ -> (Play) -> JUEGO -> (muerte) -> GAME OVER -> (Quit/R) -> MENÚ
	  \-> (Shop) -> TIENDA -> (ESC) -> MENÚ
```

## Mecánicas clave
- **Obstáculos**: si chocan contigo y no hay poder activo, mueres.
- **Anillos**: suman puntuación y al morir se convierten en monedas (persisten en la BD SQLite) para comprar skins.
- **Corazones**: al juntar 5 activas poder “thank u, next” (invencibilidad + más velocidad + más spawns).
- **Skins**: Original gratis, Dangerous Woman (500 monedas), otras dos marcadas “Próximamente”. Selección persistente.
- **Poder**: dura 15 s; limpia corazones al final; duplica velocidad de scroll.

## Cómo se “gana” y cómo se pierde
- Es infinito: ganar = sobrevivir y lograr mayor distancia/anillos.
- Pierdes al chocar con un obstáculo sin poder activo. Al morir se guardan puntaje y monedas acumuladas.

