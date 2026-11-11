import json
import math
import os
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import pygame
except ImportError:
    print("Dependencia ausente: pygame. Instale com: python -m pip install pygame")
    raise SystemExit(1)

# -----------------------------------------------------------------------------
# Configuracao
# -----------------------------------------------------------------------------
WIDTH, HEIGHT = 1280, 760
PANEL_X = 965
PANEL_W = WIDTH - PANEL_X
FPS = 60
SAVE_FILE = Path(__file__).with_name("jungle_defense_save.json")
TITLE = "JUNGLE DEFENSE"

COLORS = {
    "ink": (37, 47, 39), "cream": (247, 239, 207), "panel": (31, 61, 47),
    "panel2": (42, 79, 58), "leaf": (48, 119, 67), "leaf2": (83, 157, 76),
    "gold": (255, 204, 74), "red": (218, 66, 56), "white": (250, 247, 225),
    "muted": (180, 199, 174), "blue": (71, 154, 210), "purple": (155, 99, 195),
    "orange": (220, 139, 55), "green": (79, 171, 105),
}

# Caminho central da partida. As torres podem ser posicionadas fora dele.
PATH = [
    (45, 425), (190, 425), (190, 205), (415, 205),
    (415, 565), (635, 565), (635, 330), (840, 330), (920, 425),
]

# Precos e desbloqueios sao valores de balanceamento deste prototipo.
TOWER_SPECS = {
    "dart": dict(name="Macaco Arqueiro", short="Arqueiro", cls="Primaria", price=200, unlock=1, color=(192, 127, 78), range=155, rate=0.68, damage=1, pierce=2, kind="normal", desc="Disparos rapidos e baratos."),
    "tack": dict(name="Macaco de Tachas", short="Tachas", cls="Primaria", price=280, unlock=3, color=(191, 101, 75), range=100, rate=1.10, damage=1, pierce=1, kind="sharp", desc="Dispara em varias direcoes."),
    "boomer": dict(name="Macaco Bumerangue", short="Bumerangue", cls="Primaria", price=325, unlock=4, color=(180, 132, 72), range=165, rate=0.90, damage=1, pierce=4, kind="sharp", desc="Ataque curvo com boa perfuracao."),
    "bomb": dict(name="Macaco Bombardeiro", short="Bombardeiro", cls="Primaria", price=525, unlock=6, color=(91, 102, 116), range=175, rate=1.45, damage=2, pierce=8, kind="explosive", splash=62, desc="Explosoes em area."),
    "ice": dict(name="Macaco Glacial", short="Glacial", cls="Primaria", price=250, unlock=8, color=(116, 190, 218), range=108, rate=2.0, damage=1, pierce=6, kind="freeze", desc="Congela inimigos proximos."),
    "glue": dict(name="Macaco Cola-Cola", short="Cola", cls="Primaria", price=275, unlock=10, color=(154, 192, 88), range=150, rate=1.15, damage=1, pierce=1, kind="glue", desc="Reduz a velocidade dos alvos."),
    "sniper": dict(name="Macaco Atirador", short="Atirador", cls="Militar", price=350, unlock=12, color=(79, 119, 86), range=999, rate=1.65, damage=2, pierce=1, kind="normal", global_range=True, desc="Alcance global; ignora obstaculos."),
    "sub": dict(name="Macaco Submarino", short="Submarino", cls="Militar", price=325, unlock=14, color=(62, 134, 157), range=220, rate=0.85, damage=1, pierce=3, kind="energy", desc="Torre naval com deteccao especial."),
    "wizard": dict(name="Macaco Mago", short="Mago", cls="Magica", price=375, unlock=16, color=(126, 90, 176), range=165, rate=1.0, damage=2, pierce=3, kind="fire", desc="Magia e fogo contra os baloes."),
    "ninja": dict(name="Macaco Ninja", short="Ninja", cls="Magica", price=500, unlock=18, color=(75, 76, 105), range=175, rate=0.58, damage=1, pierce=3, kind="sharp", camo=True, desc="Detecta e ataca camuflados."),
    "alchemist": dict(name="Macaco Alquimista", short="Alquimista", cls="Magica", price=400, unlock=20, color=(183, 129, 55), range=145, rate=1.25, damage=1, pierce=1, kind="acid", desc="Fortalece torres proximas."),
    "farm": dict(name="Fazenda Tropical", short="Fazenda", cls="Suporte", price=1250, unlock=22, color=(100, 160, 80), range=0, rate=0, damage=0, pierce=0, kind="farm", desc="Gera moedas ao fim de cada onda."),
    "village": dict(name="Vila dos Macacos", short="Vila", cls="Suporte", price=1200, unlock=24, color=(196, 133, 57), range=145, rate=0, damage=0, pierce=0, kind="village", desc="Amplia alcance e revela camuflados."),
    "engineer": dict(name="Macaco Engenheiro", short="Engenheiro", cls="Suporte", price=400, unlock=26, color=(179, 137, 75), range=150, rate=0.82, damage=1, pierce=2, kind="normal", desc="Construtor versatil de defesa."),
}

BALLOON_TYPES = {
    "Vermelho": dict(color=(224, 61, 55), hp=1, speed=72, reward=1, children=[]),
    "Azul": dict(color=(64, 139, 222), hp=2, speed=82, reward=1, children=["Vermelho"]),
    "Verde": dict(color=(73, 183, 92), hp=3, speed=91, reward=1, children=["Azul"]),
    "Amarelo": dict(color=(247, 207, 61), hp=4, speed=130, reward=1, children=["Verde"]),
    "Rosa": dict(color=(236, 116, 163), hp=5, speed=150, reward=1, children=["Amarelo"]),
    "Roxo": dict(color=(154, 88, 190), hp=8, speed=108, reward=2, children=["Rosa"], immune={"fire", "energy", "plasma"}),
    "Preto": dict(color=(52, 54, 63), hp=11, speed=100, reward=2, children=["Rosa", "Rosa"], immune={"explosive"}),
    "Branco": dict(color=(245, 245, 235), hp=11, speed=104, reward=2, children=["Rosa", "Rosa"], immune={"freeze"}),
    "Chumbo": dict(color=(116, 129, 143), hp=18, speed=62, reward=3, children=["Preto", "Preto"], immune={"sharp"}),
    "Ceramico": dict(color=(183, 112, 69), hp=32, speed=85, reward=4, children=["Roxo", "Roxo", "Roxo"]),
    "MOAB": dict(color=(90, 149, 218), hp=170, speed=38, reward=18, children=["Ceramico"] * 4, moab=True),
}

# -----------------------------------------------------------------------------
# Utilitarios e salvamento
# -----------------------------------------------------------------------------
def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def round_price(value: float) -> int:
    return int(round(value / 5.0) * 5)


def load_save() -> dict:
    default = {
        "account_level": 1, "account_xp": 0, "monkey_money": 0,
        "tower_xp": {key: 0 for key in TOWER_SPECS},
        "unlocked_towers": ["dart"], "games": 0, "wins": 0,
        "total_pops": 0, "unlocked_heroes": ["quincy"], "best_wave": 0,
    }
    try:
        if SAVE_FILE.exists():
            data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
            for key, val in default.items():
                if key not in data:
                    data[key] = val
            for key in TOWER_SPECS:
                data["tower_xp"].setdefault(key, 0)
            data["unlocked_towers"] = list(dict.fromkeys(data["unlocked_towers"] + ["dart"]))
            return data
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return default


def save_game(data: dict) -> None:
    try:
        SAVE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        print("Aviso: nao foi possivel salvar o progresso.")


def xp_for_next_level(level: int) -> int:
    return 100 + (level - 1) * 55


def account_level_from_xp(xp: int) -> tuple[int, int]:
    level, remaining = 1, max(0, xp)
    while remaining >= xp_for_next_level(level):
        remaining -= xp_for_next_level(level)
        level += 1
    return level, remaining

# -----------------------------------------------------------------------------
# Elementos do jogo
# -----------------------------------------------------------------------------
@dataclass
class Balloon:
    name: str
    x: float
    y: float
    path_index: int = 0
    progress: float = 0.0
    hp: int = 1
    max_hp: int = 1
    speed: float = 70.0
    reward: int = 1
    children: list[str] = field(default_factory=list)
    immune: set[str] = field(default_factory=set)
    camo: bool = False
    regrow: bool = False
    regrow_timer: float = 0.0
    slow_timer: float = 0.0
    stun_timer: float = 0.0
    freeze_timer: float = 0.0
    moab: bool = False
    dead: bool = False
    escaped: bool = False
    regrow_phase: float = 0.0

    @classmethod
    def create(cls, name: str, camo: bool = False, regrow: bool = False) -> "Balloon":
        info = BALLOON_TYPES[name]
        return cls(name, float(PATH[0][0]), float(PATH[0][1]), hp=info["hp"], max_hp=info["hp"],
                   speed=info["speed"], reward=info["reward"], children=list(info.get("children", [])),
                   immune=set(info.get("immune", set())), camo=camo, regrow=regrow,
                   moab=info.get("moab", False))

    def move(self, dt: float) -> None:
        if self.dead or self.escaped:
            return
        if self.stun_timer > 0:
            self.stun_timer = max(0.0, self.stun_timer - dt)
            return
        if self.freeze_timer > 0:
            self.freeze_timer = max(0.0, self.freeze_timer - dt)
            return
        if self.slow_timer > 0:
            self.slow_timer = max(0.0, self.slow_timer - dt)
            speed_factor = 0.48
        else:
            speed_factor = 1.0
        self.regrow_phase += dt
        if self.regrow and self.regrow_phase > 2.4 and self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + 1)
            self.regrow_phase = 0
        self.progress += self.speed * speed_factor * dt
        while self.path_index < len(PATH) - 1:
            a, b = PATH[self.path_index], PATH[self.path_index + 1]
            seg_len = distance(a, b)
            if self.progress <= seg_len:
                t = self.progress / max(1, seg_len)
                self.x = a[0] + (b[0] - a[0]) * t
                self.y = a[1] + (b[1] - a[1]) * t
                break
            self.progress -= seg_len
            self.path_index += 1
        if self.path_index >= len(PATH) - 1:
            self.x, self.y = PATH[-1]
            self.escaped = True

    def damage(self, amount: int, damage_type: str) -> int:
        if self.dead or damage_type in self.immune:
            return 0
        old = self.hp
        self.hp -= max(0, amount)
        if self.hp <= 0:
            self.dead = True
        return old - max(0, self.hp)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if self.dead or self.escaped:
            return
        x, y = int(self.x), int(self.y)
        color = BALLOON_TYPES[self.name]["color"]
        if self.moab:
            # Dirigivel cartoon.
            pygame.draw.ellipse(surface, (48, 87, 135), (x - 27, y - 16, 56, 34))
            pygame.draw.ellipse(surface, color, (x - 30, y - 21, 56, 34))
            pygame.draw.line(surface, (228, 225, 192), (x - 2, y + 13), (x - 2, y + 25), 2)
            pygame.draw.rect(surface, (190, 174, 133), (x - 8, y + 23, 14, 8), border_radius=3)
            pygame.draw.ellipse(surface, (255, 255, 255), (x - 17, y - 12, 12, 7))
            pygame.draw.ellipse(surface, (40, 50, 60), (x - 12, y - 10, 4, 4))
        else:
            pygame.draw.ellipse(surface, color, (x - 10, y - 14, 21, 27))
            pygame.draw.ellipse(surface, tuple(min(255, c + 45) for c in color), (x - 6, y - 10, 7, 9))
            pygame.draw.line(surface, (226, 222, 195), (x, y + 12), (x + 2, y + 24), 2)
            pygame.draw.ellipse(surface, (255, 255, 255), (x + 1, y - 5, 6, 7))
            pygame.draw.circle(surface, (35, 35, 35), (x + 5, y - 1), 2)
        if self.camo:
            pygame.draw.arc(surface, (38, 44, 49), (x - 16, y - 20, 32, 39), 0, math.pi * 2, 2)
            pygame.draw.line(surface, (30, 35, 34), (x - 12, y + 15), (x + 12, y - 15), 2)
        if self.regrow:
            pygame.draw.circle(surface, (120, 244, 150), (x + 10, y - 13), 4, 2)
        if self.stun_timer > 0 or self.freeze_timer > 0:
            pygame.draw.circle(surface, (179, 231, 248), (x, y - 22), 5, 2)
        # Barra curta de vida para ceramicos e MOABs.
        if self.moab or self.max_hp > 15:
            w = 52 if self.moab else 25
            pygame.draw.rect(surface, (55, 45, 45), (x - w // 2, y - 31, w, 5), border_radius=2)
            pygame.draw.rect(surface, (93, 207, 105), (x - w // 2, y - 31, int(w * max(0, self.hp) / self.max_hp), 5), border_radius=2)


@dataclass
class Projectile:
    x: float
    y: float
    target: Balloon
    speed: float
    damage: int
    pierce: int
    damage_type: str
    color: tuple[int, int, int]
    splash: float = 0
    freeze: float = 0
    slow: float = 0
    camo_pierce: bool = False
    trail: list[tuple[float, float]] = field(default_factory=list)
    dead: bool = False
    hit_ids: set[int] = field(default_factory=set)

    def update(self, dt: float, game: "Game") -> None:
        if self.dead:
            return
        if self.target.dead or self.target.escaped:
            # O projétil nao persegue outro alvo; desaparece suavemente.
            self.dead = True
            return
        dx, dy = self.target.x - self.x, self.target.y - self.y
        dist = math.hypot(dx, dy)
        step = self.speed * dt
        if dist <= max(8, step):
            self.x, self.y = self.target.x, self.target.y
            hit_target = self.target
            self.hit_ids.add(id(hit_target))
            game.projectile_hit(self, hit_target)
            self.pierce -= 1
            # Um projétil pode atravessar alvos próximos, consumindo Pierce.
            next_targets = [b for b in game.balloons
                            if not b.dead and not b.escaped and id(b) not in self.hit_ids
                            and (not b.camo or self.camo_pierce or game.near_village(b.x, b.y))
                            and distance((self.x, self.y), (b.x, b.y)) <= 72]
            if self.pierce > 0 and next_targets:
                self.target = min(next_targets, key=lambda b: distance((self.x, self.y), (b.x, b.y)))
            else:
                self.dead = True
        elif dist > 0:
            self.x += dx / dist * step
            self.y += dy / dist * step
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)

    def draw(self, surface: pygame.Surface) -> None:
        if self.dead:
            return
        if len(self.trail) > 1:
            pygame.draw.lines(surface, self.color, False, self.trail, 2)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 5)
        pygame.draw.circle(surface, (255, 248, 211), (int(self.x) - 1, int(self.y) - 1), 2)


@dataclass
class Tower:
    key: str
    x: float
    y: float
    path_levels: list[int] = field(default_factory=lambda: [0, 0, 0])
    cooldown: float = 0.0
    angle: float = 0.0
    anim: float = 0.0
    target_mode: str = "Primeiro"
    pop_count: int = 0
    invested: int = 0
    buff_timer: float = 0.0
    buff_strength: float = 0.0
    selected: bool = False
    farm_bank: int = 0

    @property
    def spec(self) -> dict:
        return TOWER_SPECS[self.key]

    @property
    def tier(self) -> int:
        return sum(self.path_levels)

    def stat(self, field_name: str):
        base = self.spec.get(field_name, 0)
        levels = self.path_levels
        if field_name == "range":
            return base + levels[0] * 11 + levels[1] * 4
        if field_name == "damage":
            return base + levels[0] // 2 + (1 if levels[2] >= 3 else 0)
        if field_name == "pierce":
            return base + levels[1] * 2
        if field_name == "rate":
            return max(0.22, base * (1 - levels[1] * 0.09) * (0.72 if self.buff_timer > 0 else 1))
        return base

    def upgrade_cost(self, path: int) -> int:
        next_tier = self.path_levels[path] + 1
        return int(self.spec["price"] * (0.42 + next_tier * 0.48) + next_tier * next_tier * 65)

    def can_upgrade(self, path: int) -> bool:
        levels = self.path_levels
        if levels[path] >= 5:
            return False
        if max(levels) >= 3 and levels[path] == 0 and any(v >= 3 for v in levels):
            return False
        if sum(1 for v in levels if v > 0) >= 2 and levels[path] == 0:
            return False
        if levels[path] < 2:
            return True
        return all(i == path or v <= 2 for i, v in enumerate(levels)) and levels[path] < 5

    def attack(self, game: "Game", dt: float) -> None:
        if self.cooldown > 0:
            self.cooldown -= dt
        self.anim = max(0, self.anim - dt * 3.5)
        if self.buff_timer > 0:
            self.buff_timer = max(0, self.buff_timer - dt)
        if self.key in ("farm", "village"):
            return
        if self.key == "alchemist" and self.cooldown <= 0:
            for other in game.towers:
                if other is not self and distance((self.x, self.y), (other.x, other.y)) < self.stat("range"):
                    other.buff_timer = max(other.buff_timer, 3.5)
                    other.buff_strength = 0.25
            self.cooldown = 3.5
        targets = []
        r = self.stat("range")
        for balloon in game.balloons:
            if balloon.dead or balloon.escaped:
                continue
            if balloon.camo and not (self.spec.get("camo") or game.near_village(self.x, self.y)):
                continue
            if not self.spec.get("global_range") and distance((self.x, self.y), (balloon.x, balloon.y)) > r:
                continue
            if not self.spec.get("global_range") and not game.has_line_of_sight(self, balloon):
                continue
            targets.append(balloon)
        if not targets or self.cooldown > 0:
            return
        if self.target_mode == "Primeiro":
            target = max(targets, key=lambda b: b.path_index * 10000 + b.progress)
        elif self.target_mode == "Ultimo":
            target = min(targets, key=lambda b: b.path_index * 10000 + b.progress)
        elif self.target_mode == "Forte":
            target = max(targets, key=lambda b: b.hp)
        else:
            target = min(targets, key=lambda b: distance((self.x, self.y), (b.x, b.y)))
        self.angle = math.atan2(target.y - self.y, target.x - self.x)
        self.anim = 1.0
        rate = self.stat("rate")
        if self.key == "tack":
            self.cooldown = rate
            # Disparo radial: cada direcao procura um alvo em seu setor.
            for i in range(8):
                angle = i * math.pi / 4
                candidates = []
                for b in targets:
                    if distance((self.x, self.y), (b.x, b.y)) > r:
                        continue
                    target_angle = math.atan2(b.y - self.y, b.x - self.x)
                    delta = abs((target_angle - angle + math.pi) % (2 * math.pi) - math.pi)
                    if delta < math.pi / 5:
                        candidates.append(b)
                if candidates:
                    radial_target = min(candidates, key=lambda b: distance((self.x, self.y), (b.x, b.y)))
                    game.projectiles.append(Projectile(self.x, self.y, radial_target, 530,
                                                       self.stat("damage"), 1, self.spec["kind"],
                                                       (255, 179, 75), camo_pierce=bool(self.spec.get("camo"))))
        elif self.key == "ice":
            self.cooldown = rate
            for b in targets:
                if distance((self.x, self.y), (b.x, b.y)) < r * 0.9 and "freeze" not in b.immune:
                    b.freeze_timer = max(b.freeze_timer, 0.85)
                    b.hp -= self.stat("damage")
                    if b.hp <= 0:
                        game.pop_balloon(b, self)
        elif self.key == "glue":
            self.cooldown = rate
            game.projectiles.append(Projectile(self.x, self.y, target, 440, self.stat("damage"),
                                               self.stat("pierce"), "glue", (151, 205, 89), slow=2.7,
                                               camo_pierce=bool(self.spec.get("camo"))))
        elif self.key == "bomb":
            self.cooldown = rate
            game.projectiles.append(Projectile(self.x, self.y, target, 330, self.stat("damage"),
                                               self.stat("pierce"), "explosive", (239, 112, 59), splash=58))
        else:
            self.cooldown = rate
            color = {
                "dart": (249, 226, 159), "boomer": (242, 168, 72), "sniper": (247, 239, 197),
                "sub": (111, 209, 225), "wizard": (188, 116, 246), "ninja": (202, 205, 220),
                "alchemist": (151, 219, 106), "engineer": (245, 198, 105),
            }.get(self.key, (246, 230, 167))
            kind = self.spec["kind"]
            if self.key == "alchemist":
                # Poção: aplica dano acido e buff em torres proximas.
                for other in game.towers:
                    if other is not self and distance((self.x, self.y), (other.x, other.y)) < r:
                        other.buff_timer = max(other.buff_timer, 4.0)
                        other.buff_strength = 0.25
            game.projectiles.append(Projectile(self.x, self.y, target, 480, self.stat("damage"),
                                               self.stat("pierce"), kind, color,
                                               camo_pierce=bool(self.spec.get("camo"))))

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, selected: bool = False) -> None:
        x, y = int(self.x), int(self.y)
        spec = self.spec
        if selected:
            pygame.draw.circle(surface, (255, 237, 139), (x, y), int(self.stat("range")), 2)
        if self.buff_timer > 0:
            pygame.draw.circle(surface, (114, 226, 139), (x, y), 27, 2)
        # Sombra e corpo do macaco.
        pygame.draw.ellipse(surface, (28, 63, 39), (x - 22, y + 13, 44, 13))
        body = spec["color"]
        pygame.draw.circle(surface, body, (x, y), 20)
        pygame.draw.circle(surface, tuple(max(0, c - 28) for c in body), (x - 13, y + 4), 10)
        # Orelhas, rosto, olhos.
        pygame.draw.circle(surface, body, (x - 17, y - 12), 8)
        pygame.draw.circle(surface, body, (x + 17, y - 12), 8)
        pygame.draw.circle(surface, (241, 205, 159), (x, y + 2), 13)
        pygame.draw.circle(surface, (255, 255, 255), (x - 5, y - 4), 4)
        pygame.draw.circle(surface, (255, 255, 255), (x + 5, y - 4), 4)
        pygame.draw.circle(surface, (34, 37, 32), (x - 4, y - 3), 2)
        pygame.draw.circle(surface, (34, 37, 32), (x + 6, y - 3), 2)
        pygame.draw.arc(surface, (118, 68, 48), (x - 5, y + 1, 10, 7), 0, math.pi, 2)
        # Equipamento e braco animado.
        arm_len = 14 + int(self.anim * 7)
        ex = x + int(math.cos(self.angle) * arm_len)
        ey = y + int(math.sin(self.angle) * arm_len)
        pygame.draw.line(surface, (232, 192, 140), (x + 8, y + 7), (ex, ey), 6)
        pygame.draw.circle(surface, (88, 63, 45), (ex, ey), 4)
        if self.key in ("dart", "ninja", "sniper", "sub"):
            pygame.draw.line(surface, (75, 65, 50), (ex, ey), (ex + 10, ey - 3), 3)
        elif self.key == "wizard":
            pygame.draw.line(surface, (100, 67, 142), (x + 14, y - 10), (x + 18, y - 31), 4)
            pygame.draw.circle(surface, (192, 124, 255), (x + 18, y - 33), 5)
        elif self.key == "bomb":
            pygame.draw.circle(surface, (64, 69, 77), (ex + 3, ey), 6)
        elif self.key == "farm":
            pygame.draw.circle(surface, (255, 216, 86), (x + 15, y - 17), 6)
        elif self.key == "village":
            pygame.draw.polygon(surface, (186, 112, 62), [(x - 14, y - 18), (x, y - 33), (x + 14, y - 18)])
        if self.tier > 0:
            pygame.draw.circle(surface, COLORS["gold"], (x + 16, y + 15), 5)
            pygame.draw.circle(surface, (70, 54, 30), (x + 16, y + 15), 5, 1)
        if selected:
            pygame.draw.circle(surface, (255, 246, 197), (x, y), 25, 2)

# -----------------------------------------------------------------------------
# Jogo
# -----------------------------------------------------------------------------
class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 18)
        self.small = pygame.font.SysFont("arial", 14)
        self.big = pygame.font.SysFont("arial", 44, bold=True)
        self.medium = pygame.font.SysFont("arial", 25, bold=True)
        self.save = load_save()
        self.towers: list[Tower] = []
        self.balloons: list[Balloon] = []
        self.projectiles: list[Projectile] = []
        self.particles: list[dict] = []
        self.selected_tower: Optional[Tower] = None
        self.build_key: Optional[str] = None
        self.money = 650
        self.lives = 100
        self.wave = 0
        self.wave_active = False
        self.spawn_queue: list[tuple[str, bool, bool, float]] = []
        self.spawn_timer = 0.0
        self.wave_elapsed = 0.0
        self.state = "menu"
        self.paused = False
        self.speed = 1
        self.account_level = self.save["account_level"]
        self.hero_unlocked = list(self.save.get("unlocked_heroes", ["quincy"]))
        self.hero = {"name": "Kiko Arqueiro", "x": 125.0, "y": 360.0, "level": 1,
                     "xp": 0, "cooldown": 0.0, "anim": 0.0}
        self.message = "Escolha um macaco na lateral e clique na selva para posiciona-lo."
        self.message_timer = 6.0
        self.bg_decor = self.make_decor()
        self.buttons: dict[str, pygame.Rect] = {}
        self.hover_text = ""
        self.end_reason = ""
        self.total_pops_this_game = 0
        self.start_ticks = pygame.time.get_ticks()

    def make_decor(self) -> list[dict]:
        rng = random.Random(14)
        decor = []
        for _ in range(120):
            decor.append({"x": rng.randint(0, PANEL_X), "y": rng.randint(25, HEIGHT - 20),
                          "r": rng.randint(7, 23), "kind": rng.choice(["leaf", "flower", "rock"]),
                          "phase": rng.random() * 6.28})
        return decor

    def toast(self, text: str, duration: float = 3.0) -> None:
        self.message, self.message_timer = text, duration

    def tower_price(self, key: str, difficulty: str = "Media") -> int:
        mult = {"Facil": 0.85, "Media": 1.0, "Dificil": 1.08, "Impoppable": 1.2}.get(difficulty, 1.0)
        return round_price(TOWER_SPECS[key]["price"] * mult)

    def add_particle(self, x: float, y: float, color: tuple[int, int, int], count: int = 8) -> None:
        for _ in range(count):
            angle = random.random() * math.tau
            speed = random.uniform(30, 115)
            self.particles.append({"x": x, "y": y, "vx": math.cos(angle) * speed,
                                  "vy": math.sin(angle) * speed, "life": random.uniform(.25, .65),
                                  "max": .65, "color": color, "r": random.randint(2, 4)})

    def can_place(self, x: int, y: int, key: str) -> bool:
        if x < 28 or x > PANEL_X - 30 or y < 60 or y > HEIGHT - 35:
            return False
        for a, b in zip(PATH, PATH[1:]):
            if self.point_segment_distance((x, y), a, b) < 42:
                return False
        if any(distance((x, y), (t.x, t.y)) < 48 for t in self.towers):
            return False
        # Regiao azul decorativa no canto representa lago; submarino so pode nela.
        if key == "sub":
            return 650 < x < 895 and 70 < y < 190
        if 650 < x < 895 and 70 < y < 190:
            return False
        return True

    @staticmethod
    def point_segment_distance(p, a, b) -> float:
        px, py = p; ax, ay = a; bx, by = b
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return distance(p, a)
        t = clamp(((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy), 0, 1)
        return distance(p, (ax + t * dx, ay + t * dy))

    def has_line_of_sight(self, tower: Tower, balloon: Balloon) -> bool:
        # Arvore grande central bloqueia tiros diretos. Artilharia global ignora.
        obstacle = (305, 365, 64)
        return self.point_segment_distance((obstacle[0], obstacle[1]), (tower.x, tower.y), (balloon.x, balloon.y)) > obstacle[2]

    def near_village(self, x: float, y: float) -> bool:
        return any(t.key == "village" and distance((x, y), (t.x, t.y)) < t.stat("range") for t in self.towers)

    def place_tower(self, x: int, y: int) -> None:
        if not self.build_key:
            return
        key = self.build_key
        if key not in self.save["unlocked_towers"]:
            self.toast("Esse macaco ainda esta bloqueado.")
            return
        price = self.tower_price(key)
        if self.money < price:
            self.toast("Dinheiro insuficiente!")
            return
        if not self.can_place(x, y, key):
            self.toast("Local invalido: evite a trilha e outras torres.")
            return
        self.money -= price
        tower = Tower(key, x, y, invested=price)
        self.towers.append(tower)
        self.selected_tower = tower
        self.build_key = None
        self.toast(f"{tower.spec['name']} posicionado!")

    def start_wave(self) -> None:
        if self.wave_active or self.state != "playing":
            return
        self.wave += 1
        self.wave_active = True
        self.wave_elapsed = 0
        self.spawn_queue = self.make_wave(self.wave)
        self.spawn_timer = 0
        self.toast(f"ONDA {self.wave} — prepare sua defesa!", 2.2)

    def make_wave(self, wave: int) -> list[tuple[str, bool, bool, float]]:
        queue = []
        amount = 6 + wave * 2
        for i in range(amount):
            if wave < 3:
                name = "Vermelho"
            elif wave < 5:
                name = random.choice(["Vermelho", "Azul"])
            elif wave < 8:
                name = random.choice(["Azul", "Verde", "Amarelo"])
            elif wave < 11:
                name = random.choice(["Verde", "Amarelo", "Rosa", "Preto"])
            elif wave < 15:
                name = random.choice(["Amarelo", "Rosa", "Roxo", "Branco", "Chumbo"])
            elif wave < 20:
                name = random.choice(["Rosa", "Roxo", "Preto", "Branco", "Chumbo", "Ceramico"])
            else:
                name = random.choice(["Rosa", "Roxo", "Preto", "Chumbo", "Ceramico"])
            camo = wave >= 12 and random.random() < 0.12
            regrow = wave >= 10 and random.random() < 0.10
            queue.append((name, camo, regrow, random.uniform(0, 0.28)))
        if wave % 5 == 0:
            queue.extend([("MOAB", False, False, 0.5), ("Ceramico", False, False, 0.4)])
        return queue

    def spawn_balloon(self, name: str, camo=False, regrow=False) -> None:
        self.balloons.append(Balloon.create(name, camo, regrow))

    def projectile_hit(self, projectile: Projectile, target: Balloon) -> None:
        if target.dead or target.escaped:
            return
        if target.camo and not projectile.camo_pierce and not self.near_village(target.x, target.y):
            return
        amount = target.damage(projectile.damage, projectile.damage_type)
        if projectile.slow:
            target.slow_timer = max(target.slow_timer, projectile.slow)
        if projectile.freeze:
            target.freeze_timer = max(target.freeze_timer, projectile.freeze)
        if amount > 0:
            self.add_particle(target.x, target.y, projectile.color, 4)
            if target.dead:
                self.pop_balloon(target, None)
        if projectile.splash > 0:
            for other in self.balloons:
                if other is not target and not other.dead and distance((target.x, target.y), (other.x, other.y)) < projectile.splash:
                    dealt = other.damage(max(1, projectile.damage - 1), projectile.damage_type)
                    if other.dead:
                        self.pop_balloon(other, None)
                    elif dealt:
                        self.add_particle(other.x, other.y, projectile.color, 2)

    def pop_balloon(self, balloon: Balloon, tower: Optional[Tower]) -> None:
        if balloon.dead is False:
            balloon.dead = True
        self.money += balloon.reward
        self.total_pops_this_game += 1
        self.save["total_pops"] = self.save.get("total_pops", 0) + 1
        if tower:
            tower.pop_count += 1
        color = BALLOON_TYPES[balloon.name]["color"]
        self.add_particle(balloon.x, balloon.y, color, 7)
        for child_name in balloon.children:
            child = Balloon.create(child_name)
            child.x, child.y = balloon.x, balloon.y
            child.path_index = balloon.path_index
            child.progress = balloon.progress
            self.balloons.append(child)

    def award_wave(self) -> None:
        # Bonus de fim de onda e renda das fazendas.
        self.money += 100 + self.wave
        farm_income = 0
        for t in self.towers:
            if t.key == "farm":
                income = 95 + t.path_levels[0] * 75 + t.path_levels[2] * 105
                farm_income += income
                t.farm_bank += income
        self.money += farm_income
        # XP de conta e XP de torres, proporcional ao investimento em campo.
        account_gain = 45 + self.wave * 4
        self.save["account_xp"] += account_gain
        invested: dict[str, int] = {}
        for t in self.towers:
            invested[t.key] = invested.get(t.key, 0) + max(1, t.invested)
        total = sum(invested.values())
        total_tower_xp = 32 + self.wave * 2
        if total:
            for key, value in invested.items():
                self.save["tower_xp"][key] = self.save["tower_xp"].get(key, 0) + int(total_tower_xp * value / total)
        level, rem = account_level_from_xp(self.save["account_xp"])
        old_level = self.save["account_level"]
        self.save["account_level"] = level
        self.account_level = level
        if level > old_level:
            self.toast(f"NIVEL {level}! Novos macacos podem ter sido desbloqueados.", 4)
        self.update_unlocks()
        self.save["best_wave"] = max(self.save.get("best_wave", 0), self.wave)
        save_game(self.save)
        self.wave_active = False
        self.toast(f"Onda concluida! +${100 + self.wave} | +{account_gain} XP | Fazenda +${farm_income}", 3.5)

    def update_unlocks(self) -> None:
        for key, spec in TOWER_SPECS.items():
            if self.account_level >= spec["unlock"] and key not in self.save["unlocked_towers"]:
                self.save["unlocked_towers"].append(key)
        if self.account_level >= 14 and "fire" not in self.hero_unlocked:
            self.hero_unlocked.append("fire")
        if self.account_level >= 21 and "commander" not in self.hero_unlocked:
            self.hero_unlocked.append("commander")
        if self.account_level >= 28 and "nature" not in self.hero_unlocked:
            self.hero_unlocked.append("nature")
        self.save["unlocked_heroes"] = self.hero_unlocked

    def update(self, dt: float) -> None:
        if self.state != "playing" or self.paused:
            return
        dt *= self.speed
        if self.message_timer > 0:
            self.message_timer -= dt
        if self.wave_active:
            self.wave_elapsed += dt
            if self.spawn_queue:
                self.spawn_timer -= dt
                if self.spawn_timer <= 0:
                    name, camo, regrow, delay = self.spawn_queue.pop(0)
                    self.spawn_balloon(name, camo, regrow)
                    self.spawn_timer = 0.52 + delay
            for b in self.balloons:
                b.move(dt)
                if b.escaped and not b.dead:
                    b.dead = True
                    self.lives -= 1
                    self.add_particle(b.x, b.y, (230, 75, 62), 8)
            for tower in self.towers:
                tower.attack(self, dt)
            for projectile in self.projectiles:
                projectile.update(dt, self)
            self.projectiles = [p for p in self.projectiles if not p.dead]
            self.balloons = [b for b in self.balloons if not b.dead and not b.escaped]
            if not self.spawn_queue and not self.balloons:
                self.award_wave()
            if self.lives <= 0:
                self.end_reason = "Sua base foi invadida!"
                self.state = "gameover"
                self.save["games"] += 1
                save_game(self.save)
        for p in self.particles:
            p["x"] += p["vx"] * dt; p["y"] += p["vy"] * dt
            p["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]
        # Heroi arqueiro: ataque automatico.
        if self.hero.get("cooldown", 0) > 0:
            self.hero["cooldown"] -= dt
        else:
            targets = [b for b in self.balloons if not b.dead and not b.escaped and (not b.camo)]
            if targets:
                target = max(targets, key=lambda b: b.path_index * 10000 + b.progress)
                self.projectiles.append(Projectile(self.hero["x"], self.hero["y"], target, 520, 1, 2,
                                                   "normal", (255, 225, 145)))
                self.hero["cooldown"] = 0.95
                self.hero["anim"] = 0.2
        self.hero["xp"] += dt * 0.8
        if self.hero["level"] < 20 and self.hero["xp"] >= self.hero["level"] * 24:
            self.hero["xp"] = 0
            self.hero["level"] += 1
            self.toast(f"{self.hero['name']} subiu para o nivel {self.hero['level']}!")

    def draw_background(self) -> None:
        self.screen.fill((100, 170, 105))
        # Camadas de vegetacao e clareiras.
        pygame.draw.rect(self.screen, (82, 147, 78), (0, 0, PANEL_X, HEIGHT))
        for i in range(8):
            y = i * 105 - 35
            pygame.draw.ellipse(self.screen, (70 + i % 2 * 8, 132 + i % 2 * 10, 70), (-90, y, 360, 150))
            pygame.draw.ellipse(self.screen, (83, 153, 78), (700, y - 40, 370, 190))
        # Lago para submarino.
        pygame.draw.ellipse(self.screen, (54, 145, 166), (645, 62, 240, 135))
        pygame.draw.ellipse(self.screen, (105, 202, 197), (668, 82, 195, 92), 3)
        # Arvore bloqueadora e troncos.
        pygame.draw.rect(self.screen, (112, 75, 46), (285, 335, 40, 135), border_radius=15)
        for ox, oy, r in [(305, 334, 67), (267, 354, 48), (341, 365, 51), (298, 290, 42)]:
            pygame.draw.circle(self.screen, (42, 102, 55), (ox, oy), r)
            pygame.draw.circle(self.screen, (61, 131, 64), (ox - 12, oy - 13), max(8, r - 15))
        # Trilha com borda de terra e interior claro.
        pygame.draw.lines(self.screen, (119, 86, 53), False, PATH, 62)
        pygame.draw.lines(self.screen, (202, 174, 116), False, PATH, 53)
        pygame.draw.lines(self.screen, (221, 195, 138), False, PATH, 43)
        # Pedrinhas na trilha.
        for i in range(18):
            px = (i * 53 + 23) % 900
            py = 428 + math.sin(i * 2.1) * 5
            pygame.draw.ellipse(self.screen, (187, 157, 104), (px, py, 8, 4))
        # Plantas decorativas.
        for d in self.bg_decor:
            x, y = int(d["x"]), int(d["y"])
            if d["kind"] == "leaf":
                pygame.draw.ellipse(self.screen, (39, 104, 57), (x, y, d["r"] * 1.8, d["r"] * .7))
                pygame.draw.line(self.screen, (114, 166, 79), (x, y + 4), (x + d["r"] * 1.5, y), 1)
            elif d["kind"] == "flower":
                pygame.draw.circle(self.screen, (239, 183, 92), (x, y), 3)
            else:
                pygame.draw.ellipse(self.screen, (102, 111, 80), (x, y, d["r"], d["r"] * .6))
        # Cipós no alto.
        for x in (30, 170, 500, 900):
            pygame.draw.arc(self.screen, (39, 104, 57), (x, -35, 45, 125), 0, 2.2, 4)
        # Indicacao do obstaculo.
        pygame.draw.circle(self.screen, (243, 211, 132), (305, 365), 65, 2)

    def draw_hero(self) -> None:
        x, y = int(self.hero["x"]), int(self.hero["y"])
        pygame.draw.ellipse(self.screen, (33, 74, 43), (x - 18, y + 13, 38, 12))
        pygame.draw.circle(self.screen, (178, 119, 72), (x, y), 18)
        pygame.draw.circle(self.screen, (236, 197, 151), (x, y + 3), 11)
        pygame.draw.circle(self.screen, (255, 255, 255), (x - 5, y - 4), 4)
        pygame.draw.circle(self.screen, (255, 255, 255), (x + 5, y - 4), 4)
        pygame.draw.circle(self.screen, (35, 35, 35), (x - 4, y - 3), 2)
        pygame.draw.circle(self.screen, (35, 35, 35), (x + 6, y - 3), 2)
        pygame.draw.line(self.screen, (101, 71, 48), (x + 10, y + 4), (x + 22, y - 9), 4)
        pygame.draw.line(self.screen, (219, 190, 125), (x + 21, y - 11), (x + 28, y - 20), 3)
        tag = self.small.render(f"{self.hero['name']} Nv.{self.hero['level']}", True, (255, 255, 235))
        self.screen.blit(tag, (x - tag.get_width() // 2, y - 43))

    def draw_panel(self) -> None:
        pygame.draw.rect(self.screen, COLORS["panel"], (PANEL_X, 0, PANEL_W, HEIGHT))
        pygame.draw.rect(self.screen, (81, 125, 79), (PANEL_X, 0, 5, HEIGHT))
        title = self.medium.render("DEFESA DA SELVA", True, COLORS["cream"])
        self.screen.blit(title, (PANEL_X + 17, 14))
        self.screen.blit(self.font.render(f"$ {self.money:,}".replace(",", "."), True, COLORS["gold"]), (PANEL_X + 18, 52))
        self.screen.blit(self.font.render(f"Vidas: {self.lives}   Onda: {self.wave}", True, COLORS["white"]), (PANEL_X + 18, 78))
        self.screen.blit(self.small.render(f"Conta Nv.{self.account_level} | XP: {self.save['account_xp']}", True, COLORS["muted"]), (PANEL_X + 18, 106))
        pygame.draw.line(self.screen, (89, 128, 91), (PANEL_X + 15, 130), (WIDTH - 15, 130), 2)
        self.buttons = {}
        # Controles principais.
        self.button("start", "INICIAR ONDA" if not self.wave_active else "ONDA EM ANDAMENTO", PANEL_X + 16, 143, PANEL_W - 32, 38,
                    (174, 128, 47) if not self.wave_active else (81, 99, 79), not self.wave_active)
        self.button("pause", "Continuar" if self.paused else "Pausar", PANEL_X + 16, 188, 104, 30, (69, 108, 78))
        self.button("speed", f"Velocidade {self.speed}x", PANEL_X + 130, 188, 139, 30, (69, 108, 78))
        self.screen.blit(self.small.render("MACACOS DISPONIVEIS", True, COLORS["gold"]), (PANEL_X + 17, 234))
        # Lista de torres em duas colunas.
        keys = list(TOWER_SPECS)
        y0 = 258
        for i, key in enumerate(keys):
            col, row = i % 2, i // 2
            x = PANEL_X + 15 + col * 132
            y = y0 + row * 45
            spec = TOWER_SPECS[key]
            unlocked = key in self.save["unlocked_towers"]
            text = f"{spec['short']} ${self.tower_price(key):,}".replace(",", ".") if unlocked else f"{spec['short']} Nv.{spec['unlock']}"
            rect = self.button("tower_" + key, text, x, y, 123, 38,
                               (70, 106, 71) if unlocked else (54, 72, 61), unlocked)
            pygame.draw.circle(self.screen, spec["color"], (x + 11, y + 19), 5)
        # Painel da torre selecionada.
        base_y = y0 + ((len(keys) + 1) // 2) * 45 + 7
        pygame.draw.line(self.screen, (89, 128, 91), (PANEL_X + 15, base_y), (WIDTH - 15, base_y), 2)
        if self.selected_tower in self.towers:
            t = self.selected_tower
            self.screen.blit(self.small.render("TORRE SELECIONADA", True, COLORS["gold"]), (PANEL_X + 17, base_y + 8))
            self.screen.blit(self.font.render(t.spec["name"], True, COLORS["white"]), (PANEL_X + 17, base_y + 29))
            self.screen.blit(self.small.render(f"Dano {t.stat('damage')} | Pierce {t.stat('pierce')} | Alcance {int(t.stat('range'))}", True, COLORS["muted"]), (PANEL_X + 17, base_y + 53))
            self.button("target", f"Alvo: {t.target_mode} (T)", PANEL_X + 16, base_y + 76, 253, 29, (69, 108, 78))
            names = ["Superior", "Intermediario", "Inferior"]
            for i in range(3):
                yy = base_y + 113 + i * 39
                cost = t.upgrade_cost(i)
                xp_ok = self.upgrade_is_unlocked(t, i)
                allowed = t.can_upgrade(i) and self.money >= cost and t.path_levels[i] < 5 and xp_ok
                label = f"{names[i]} {t.path_levels[i]}/5  ${cost}" if xp_ok else f"{names[i]} {t.path_levels[i]}/5  (XP bloqueada)"
                self.button(f"upgrade_{i}", label, PANEL_X + 16, yy, 253, 33,
                            (107, 105, 58) if allowed else (55, 75, 61), allowed)
            self.button("sell", f"Vender +${int(t.invested * 0.7)}", PANEL_X + 16, base_y + 235, 253, 31, (131, 75, 57))
        else:
            self.screen.blit(self.small.render("Selecione uma torre no mapa para", True, COLORS["muted"]), (PANEL_X + 17, base_y + 18))
            self.screen.blit(self.small.render("ver atributos, upgrades e vender.", True, COLORS["muted"]), (PANEL_X + 17, base_y + 37))
        # Rodape / progresso.
        self.screen.blit(self.small.render(f"Macacos desbloqueados: {len(self.save['unlocked_towers'])}/{len(TOWER_SPECS)}", True, COLORS["muted"]), (PANEL_X + 17, HEIGHT - 54))
        self.screen.blit(self.small.render(f"Dinheiro de Macaco: {self.save['monkey_money']}", True, COLORS["gold"]), (PANEL_X + 17, HEIGHT - 31))

    def button(self, key: str, label: str, x: int, y: int, w: int, h: int,
               color: tuple[int, int, int], enabled: bool = True) -> pygame.Rect:
        rect = pygame.Rect(x, y, w, h)
        mouse = pygame.mouse.get_pos()
        fill = tuple(min(255, int(c * (1.13 if rect.collidepoint(mouse) and enabled else 1))) for c in color)
        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        pygame.draw.rect(self.screen, (129, 157, 111) if enabled else (70, 88, 73), rect, 1, border_radius=8)
        text = self.small.render(label, True, (255, 251, 220) if enabled else (144, 157, 137))
        self.screen.blit(text, text.get_rect(center=rect.center))
        self.buttons[key] = rect
        return rect

    def draw(self) -> None:
        self.draw_background()
        if self.state == "menu":
            overlay = pygame.Surface((PANEL_X, HEIGHT), pygame.SRCALPHA)
            overlay.fill((18, 50, 33, 105))
            self.screen.blit(overlay, (0, 0))
            title = self.big.render("JUNGLE DEFENSE", True, (255, 231, 156))
            self.screen.blit(title, (PANEL_X // 2 - title.get_width() // 2, 180))
            subtitle = self.medium.render("A selva precisa de voce!", True, (255, 255, 226))
            self.screen.blit(subtitle, (PANEL_X // 2 - subtitle.get_width() // 2, 245))
            for i in range(6):
                x = 265 + i * 75
                y = 390 + math.sin(i * 1.7) * 18
                dummy = Tower("dart", x, y)
                dummy.draw(self.screen, self.small)
            self.button("play", "JOGAR", PANEL_X // 2 - 95, 500, 190, 52, (169, 124, 47))
            self.button("quit", "SAIR", PANEL_X // 2 - 95, 562, 190, 42, (85, 103, 75))
            self.screen.blit(self.font.render(f"Conta nivel {self.account_level}  |  Recorde: onda {self.save.get('best_wave', 0)}", True, (245, 240, 203)), (PANEL_X // 2 - 180, 640))
            pygame.display.flip()
            return
        for tower in self.towers:
            tower.draw(self.screen, self.font, tower is self.selected_tower)
        self.draw_hero()
        for b in self.balloons:
            b.draw(self.screen, self.small)
        for p in self.projectiles:
            p.draw(self.screen)
        for p in self.particles:
            alpha = max(0, min(255, int(255 * p["life"] / p["max"])))
            color = p["color"]
            pygame.draw.circle(self.screen, color, (int(p["x"]), int(p["y"])), p["r"])
        # Ghost de posicionamento.
        if self.build_key:
            mx, my = pygame.mouse.get_pos()
            if mx < PANEL_X:
                valid = self.can_place(mx, my, self.build_key)
                pygame.draw.circle(self.screen, (104, 227, 124) if valid else (232, 82, 70), (mx, my), 25, 2)
                pygame.draw.circle(self.screen, TOWER_SPECS[self.build_key]["color"], (mx, my), 16, 1)
        self.draw_panel()
        # HUD de mensagem.
        if self.message_timer > 0 and self.message:
            box = pygame.Rect(18, 15, min(760, self.font.size(self.message)[0] + 30), 34)
            pygame.draw.rect(self.screen, (33, 67, 46), box, border_radius=9)
            self.screen.blit(self.small.render(self.message, True, COLORS["cream"]), (box.x + 12, box.y + 9))
        if self.paused:
            veil = pygame.Surface((PANEL_X, HEIGHT), pygame.SRCALPHA); veil.fill((0, 0, 0, 95)); self.screen.blit(veil, (0, 0))
            txt = self.big.render("PAUSADO", True, COLORS["cream"])
            self.screen.blit(txt, txt.get_rect(center=(PANEL_X // 2, HEIGHT // 2)))
        if self.state == "gameover":
            veil = pygame.Surface((PANEL_X, HEIGHT), pygame.SRCALPHA); veil.fill((24, 25, 24, 175)); self.screen.blit(veil, (0, 0))
            txt = self.big.render("FIM DE JOGO", True, (255, 197, 112))
            self.screen.blit(txt, txt.get_rect(center=(PANEL_X // 2, 300)))
            sub = self.medium.render(self.end_reason, True, COLORS["white"])
            self.screen.blit(sub, sub.get_rect(center=(PANEL_X // 2, 360)))
            self.button("again", "JOGAR NOVAMENTE", PANEL_X // 2 - 120, 420, 240, 48, (160, 120, 47))
            self.button("menu", "MENU", PANEL_X // 2 - 120, 480, 240, 40, (68, 107, 76))
        pygame.display.flip()

    def select_tower(self, x: int, y: int) -> None:
        self.selected_tower = None
        for tower in reversed(self.towers):
            if distance((x, y), (tower.x, tower.y)) <= 25:
                self.selected_tower = tower
                break

    def upgrade_is_unlocked(self, tower: Tower, path: int) -> bool:
        next_tier = tower.path_levels[path] + 1
        requirements = {1: 0, 2: 80, 3: 220, 4: 550, 5: 1100}
        return self.save.get("tower_xp", {}).get(tower.key, 0) >= requirements[next_tier]

    def upgrade(self, path: int) -> None:
        t = self.selected_tower
        if not t or t not in self.towers:
            return
        if not t.can_upgrade(path):
            self.toast("Caminho bloqueado pelas regras de melhorias.")
            return
        if not self.upgrade_is_unlocked(t, path):
            self.toast("XP insuficiente para desbloquear esse nivel desta torre.")
            return
        cost = t.upgrade_cost(path)
        if self.money < cost:
            self.toast("Dinheiro insuficiente para essa melhoria.")
            return
        t.path_levels[path] += 1
        t.invested += cost
        self.money -= cost
        self.add_particle(t.x, t.y, COLORS["gold"], 16)
        self.toast(f"Melhoria comprada: {t.spec['name']} — nivel {t.path_levels[path]}!")

    def handle_click(self, pos: tuple[int, int]) -> None:
        x, y = pos
        if self.state == "menu":
            if self.buttons.get("play", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
                self.state = "playing"
                self.toast("Bem-vindo! Posicione macacos fora da trilha.", 5)
            elif self.buttons.get("quit", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
                pygame.quit(); raise SystemExit
            return
        if self.state == "gameover":
            if self.buttons.get("again", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
                self.reset_game(); return
            if self.buttons.get("menu", pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
                self.state = "menu"; return
        if x >= PANEL_X:
            for key, rect in list(self.buttons.items()):
                if not rect.collidepoint(pos):
                    continue
                if key.startswith("tower_"):
                    tower_key = key[6:]
                    if tower_key in self.save["unlocked_towers"]:
                        self.build_key = tower_key
                        self.selected_tower = None
                        self.toast(f"Clique na selva para posicionar: {TOWER_SPECS[tower_key]['name']}")
                    else:
                        self.toast(f"Desbloqueie no nivel {TOWER_SPECS[tower_key]['unlock']}.")
                elif key == "start":
                    self.start_wave()
                elif key == "pause":
                    self.paused = not self.paused
                elif key == "speed":
                    self.speed = 1 if self.speed >= 2 else self.speed + 1
                elif key == "target" and self.selected_tower:
                    modes = ["Primeiro", "Ultimo", "Forte", "Proximo"]
                    self.selected_tower.target_mode = modes[(modes.index(self.selected_tower.target_mode) + 1) % len(modes)]
                elif key.startswith("upgrade_"):
                    self.upgrade(int(key[-1]))
                elif key == "sell" and self.selected_tower:
                    t = self.selected_tower
                    self.money += int(t.invested * 0.7)
                    self.towers.remove(t)
                    self.selected_tower = None
                    self.toast("Torre vendida por 70% do investimento.")
                return
        if x < PANEL_X:
            if self.build_key:
                self.place_tower(x, y)
            else:
                self.select_tower(x, y)

    def reset_game(self) -> None:
        self.towers.clear(); self.balloons.clear(); self.projectiles.clear(); self.particles.clear()
        self.selected_tower = None; self.build_key = None
        self.money = 650; self.lives = 100; self.wave = 0; self.wave_active = False
        self.spawn_queue.clear(); self.paused = False; self.speed = 1
        self.hero.update({"x": 125.0, "y": 360.0, "level": 1, "xp": 0, "cooldown": 0.0})
        self.state = "playing"
        self.save["games"] += 1
        save_game(self.save)
        self.toast("Nova partida iniciada!")

    def handle_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            if self.build_key:
                self.build_key = None
            elif self.state == "playing":
                self.paused = not self.paused
        elif event.key == pygame.K_SPACE and self.state == "playing":
            self.start_wave()
        elif event.key == pygame.K_t and self.selected_tower:
            modes = ["Primeiro", "Ultimo", "Forte", "Proximo"]
            self.selected_tower.target_mode = modes[(modes.index(self.selected_tower.target_mode) + 1) % len(modes)]
        elif event.key == pygame.K_1:
            self.speed = 1
        elif event.key == pygame.K_2:
            self.speed = 2

    def run(self) -> None:
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.04)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_game(self.save); running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    self.build_key = None
            self.update(dt)
            self.draw()
        pygame.quit()


def main() -> None:
    Game().run()
