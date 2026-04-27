import { DragEvent, MouseEvent, useEffect, useMemo, useRef, useState } from "react";

type Gem = {
  instance_id: string;
  name_text: string;
  category_text: string;
  rarity_text: string;
  gem_type: { display_text: string; identity_text: string };
  tags: { text: string }[];
  random_affixes: Affix[];
  current_effective_targets: { name_text: string }[];
  board_position: { row: number; column: number } | null;
};

type Affix = {
  name_text: string;
  gen_text: string;
  stat: { text: string };
  value: number;
};

type Cell = {
  row: number;
  column: number;
  box: number;
  gem: Gem | null;
};

type SkillPreview = {
  active_gem_instance_id: string;
  name_text: string;
  final_damage: number;
  final_cooldown_ms: number;
  projectile_count: number;
  area_multiplier: number;
  speed_multiplier: number;
  applied_modifiers: {
    source_name_text: string;
    stat: { text: string };
    value: number;
    relation_text: string;
    reason_text: string;
  }[];
};

type AppState = {
  inventory: Gem[];
  board: {
    cells: Cell[][];
    prompts: string[];
    highlights: Record<string, { instance_ids: string[]; relation_text: string }[]>;
  };
  skill_preview: SkillPreview[];
  skill_error: string | null;
  drops: { drop_id: string; name_text: string; rarity_text: string; picked_up: boolean; status_text: string }[];
  logs: string[];
};

type Enemy = {
  id: number;
  x: number;
  y: number;
  hp: number;
  maxHp: number;
};

type FloatingText = {
  id: number;
  x: number;
  y: number;
  text: string;
  ttl: number;
};

type FireBolt = {
  id: number;
  x: number;
  y: number;
  targetX: number;
  targetY: number;
  ttl: number;
};

type Tooltip = {
  gem: Gem;
  x: number;
  y: number;
};

const MAP_WIDTH = 1600;
const MAP_HEIGHT = 960;
const PLAYER_SPEED = 250;

async function requestState(path: string, body?: unknown): Promise<AppState> {
  const response = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "操作失败。");
  return payload;
}

export function App() {
  const [state, setState] = useState<AppState | null>(null);
  const [bagOpen, setBagOpen] = useState(false);
  const [notice, setNotice] = useState("正在载入。");
  const [playing, setPlaying] = useState(false);
  const [player, setPlayer] = useState({ x: MAP_WIDTH / 2, y: MAP_HEIGHT / 2, hp: 510, maxHp: 510 });
  const [enemies, setEnemies] = useState<Enemy[]>([]);
  const [texts, setTexts] = useState<FloatingText[]>([]);
  const [bolts, setBolts] = useState<FireBolt[]>([]);
  const [kills, setKills] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [combatLogs, setCombatLogs] = useState<string[]>([]);
  const [hoveredGemId, setHoveredGemId] = useState<string | null>(null);
  const [tooltip, setTooltip] = useState<Tooltip | null>(null);
  const [draggingGemId, setDraggingGemId] = useState<string | null>(null);
  const keys = useRef(new Set<string>());
  const draggingGemIdRef = useRef<string | null>(null);
  const lastFrame = useRef<number | null>(null);
  const nextEnemyId = useRef(1);
  const nextTextId = useRef(1);
  const nextBoltId = useRef(1);
  const attackTimer = useRef(0);
  const spawnTimer = useRef(0);

  useEffect(() => {
    requestState("/api/state")
      .then((nextState) => {
        setState(nextState);
        setNotice("准备就绪。按 C 打开背包。");
      })
      .catch((error: Error) => setNotice(error.message));
  }, []);

  useEffect(() => {
    function onMouseUp(event: MouseEvent) {
      const instanceId = draggingGemIdRef.current;
      if (!instanceId) return;
      draggingGemIdRef.current = null;
      setDraggingGemId(null);
      const element = document.elementFromPoint(event.clientX, event.clientY);
      const cell = element?.closest("[data-board-row][data-board-column]") as HTMLElement | null;
      if (!cell) return;
      void dropGemOnCell(instanceId, Number(cell.dataset.boardRow), Number(cell.dataset.boardColumn));
    }
    window.addEventListener("mouseup", onMouseUp);
    return () => window.removeEventListener("mouseup", onMouseUp);
  }, [state]);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const key = event.key.toLowerCase();
      if (key === "c") {
        event.preventDefault();
        setBagOpen((current) => !current);
        setTooltip(null);
        setHoveredGemId(null);
        return;
      }
      if (["w", "a", "s", "d"].includes(key)) keys.current.add(key);
    }
    function onKeyUp(event: KeyboardEvent) {
      keys.current.delete(event.key.toLowerCase());
    }
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
    };
  }, []);

  const activeSkill = state?.skill_preview?.[0] ?? null;

  useEffect(() => {
    if (!playing) {
      lastFrame.current = null;
      return;
    }

    let frame = 0;
    function tick(now: number) {
      if (lastFrame.current === null) lastFrame.current = now;
      const dt = Math.min(0.05, (now - lastFrame.current) / 1000);
      lastFrame.current = now;
      stepGame(dt);
      frame = requestAnimationFrame(tick);
    }

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing, activeSkill, player.x, player.y, elapsed]);

  function stepGame(dt: number) {
    setElapsed((value) => value + dt);
    setPlayer((current) => {
      let dx = 0;
      let dy = 0;
      if (keys.current.has("a")) dx -= 1;
      if (keys.current.has("d")) dx += 1;
      if (keys.current.has("w")) dy -= 1;
      if (keys.current.has("s")) dy += 1;
      const length = Math.hypot(dx, dy) || 1;
      return {
        ...current,
        x: clamp(current.x + (dx / length) * PLAYER_SPEED * dt, 40, MAP_WIDTH - 40),
        y: clamp(current.y + (dy / length) * PLAYER_SPEED * dt, 40, MAP_HEIGHT - 40)
      };
    });

    spawnTimer.current -= dt;
    if (spawnTimer.current <= 0) {
      spawnTimer.current = Math.max(0.45, 1.2 - elapsed / 80);
      setEnemies((current) => [...current, createEnemy(nextEnemyId.current++, player.x, player.y)]);
    }

    setEnemies((current) =>
      current.map((enemy) => {
        const dx = player.x - enemy.x;
        const dy = player.y - enemy.y;
        const length = Math.hypot(dx, dy) || 1;
        const speed = 58;
        return { ...enemy, x: enemy.x + (dx / length) * speed * dt, y: enemy.y + (dy / length) * speed * dt };
      })
    );

    attackTimer.current -= dt;
    if (attackTimer.current <= 0 && activeSkill) {
      attackTimer.current = Math.max(0.16, activeSkill.final_cooldown_ms / 1000);
      setEnemies((current) => hitEnemies(current, activeSkill));
    }

    setTexts((current) =>
      current.map((text) => ({ ...text, ttl: text.ttl - dt, y: text.y - 22 * dt })).filter((text) => text.ttl > 0)
    );
    setBolts((current) => current.map((bolt) => ({ ...bolt, ttl: bolt.ttl - dt })).filter((bolt) => bolt.ttl > 0));
  }

  function hitEnemies(current: Enemy[], skill: SkillPreview) {
    if (current.length === 0) return current;
    const range = 520 * skill.area_multiplier;
    const targets = [...current]
      .sort((a, b) => distance(a, player) - distance(b, player))
      .filter((enemy) => distance(enemy, player) <= range)
      .slice(0, Math.max(1, skill.projectile_count));
    if (targets.length === 0) return current;

    const targetIds = new Set(targets.map((target) => target.id));
    const nextTexts: FloatingText[] = [];
    const nextBolts: FireBolt[] = targets.map((target) => ({
      id: nextBoltId.current++,
      x: player.x,
      y: player.y - 12,
      targetX: target.x,
      targetY: target.y,
      ttl: 0.42
    }));
    const survivors = current
      .map((enemy) => {
        if (!targetIds.has(enemy.id)) return enemy;
        const hp = enemy.hp - skill.final_damage;
        nextTexts.push({ id: nextTextId.current++, x: enemy.x, y: enemy.y - 28, text: Math.round(skill.final_damage).toString(), ttl: 0.8 });
        return { ...enemy, hp };
      })
      .filter((enemy) => enemy.hp > 0);
    const killed = current.length - survivors.length;
    setBolts((items) => [...items, ...nextBolts]);
    if (killed > 0) {
      setKills((value) => value + killed);
      setCombatLogs((logs) => [`${skill.name_text} 击杀 ${killed} 个怪物。`, ...logs].slice(0, 8));
    } else {
      setCombatLogs((logs) => [`${skill.name_text} 自动释放。`, ...logs].slice(0, 8));
    }
    setTexts((items) => [...items, ...nextTexts]);
    return survivors;
  }

  async function dropGemOnCell(instanceId: string, row: number, column: number) {
    if (!state) return;
    const target = state.board.cells[row]?.[column]?.gem;
    if (target && target.instance_id !== instanceId) {
      setNotice("该格已有宝石。");
      return;
    }
    const dragged = state.inventory.find((gem) => gem.instance_id === instanceId);
    if (!dragged) {
      setNotice("没有找到这颗宝石。");
      return;
    }
    if (dragged.board_position?.row === row && dragged.board_position.column === column) return;

    try {
      if (dragged.board_position) {
        await requestState("/api/unmount", { instance_id: instanceId });
      }
      const nextState = await requestState("/api/mount", { instance_id: instanceId, row, column });
      setState(nextState);
      setNotice(`已将${dragged.name_text}放入第${row + 1}行第${column + 1}列。`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "操作失败。");
    }
  }

  async function unmountGem(instanceId: string) {
    try {
      const gem = state?.inventory.find((item) => item.instance_id === instanceId);
      const nextState = await requestState("/api/unmount", { instance_id: instanceId });
      setState(nextState);
      setNotice(gem ? `已取下${gem.name_text}。` : "宝石已下盘。");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "操作失败。");
    }
  }

  async function runServerCombat() {
    try {
      const nextState = await requestState("/api/combat/start", {});
      setState(nextState);
      if (nextState.drops.length > 0) setNotice(`掉落：${nextState.drops.map((drop) => drop.name_text).join("、")}。`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "战斗结算失败。");
    }
  }

  function startGame() {
    setPlaying(true);
    setBagOpen(false);
    setEnemies([
      createEnemy(nextEnemyId.current++, player.x, player.y),
      createEnemy(nextEnemyId.current++, player.x, player.y),
      createEnemy(nextEnemyId.current++, player.x, player.y)
    ]);
    setCombatLogs(["战斗开始。WASD 移动，技能会自动释放。"]);
    setNotice("战斗中。按 C 管理背包。");
    void runServerCombat();
  }

  function beginDrag(event: DragEvent, gem: Gem) {
    event.dataTransfer.setData("text/plain", gem.instance_id);
    event.dataTransfer.effectAllowed = "move";
  }

  function beginPointerDrag(event: MouseEvent, gem: Gem) {
    if (event.button !== 0) return;
    draggingGemIdRef.current = gem.instance_id;
    setDraggingGemId(gem.instance_id);
  }

  function onGemHover(event: MouseEvent, gem: Gem) {
    setHoveredGemId(gem.instance_id);
    setTooltip({ gem, x: event.clientX, y: event.clientY });
  }

  const linkedGemIds = useLinkedGemIds(state, hoveredGemId);
  const fullGemById = useMemo(() => {
    const result = new Map<string, Gem>();
    for (const gem of state?.inventory ?? []) result.set(gem.instance_id, gem);
    return result;
  }, [state]);

  if (!state) return <main className="game-screen loading">{notice}</main>;

  return (
    <main className="game-screen">
      <section className="map-layer" aria-label="可玩地图">
        <div className="terrain" style={{ transform: `translate(${-player.x + 800}px, ${-player.y + 480}px)` }}>
          <MapTiles />
          {enemies.map((enemy) => (
            <div key={enemy.id} className="enemy" style={{ left: enemy.x, top: enemy.y }}>
              <span style={{ width: `${Math.max(0, enemy.hp / enemy.maxHp) * 100}%` }} />
            </div>
          ))}
          {bolts.map((bolt) => <FireBoltView key={bolt.id} bolt={bolt} />)}
          <div className="player" style={{ left: player.x, top: player.y }} />
          {texts.map((text) => (
            <div key={text.id} className="floating-text" style={{ left: text.x, top: text.y }}>{text.text}</div>
          ))}
        </div>
      </section>

      <header className="top-hud">
        <h1>数独宝石流放like V1</h1>
        <span>{notice}</span>
      </header>

      <div className="help-text">
        <p>C：打开/关闭背包</p>
        <p>WASD：移动</p>
        <p>拖拽：放置宝石</p>
        <p>LMB：拾取</p>
      </div>

      {!playing && (
        <button className="start-button" onClick={startGame}>开始游戏</button>
      )}

      <section className="bottom-hud" aria-label="战斗状态">
        <div className="orb life-orb">
          <strong>{Math.round(player.hp)}</strong>
          <span>生命</span>
        </div>
        <div className="orb mana-orb">
          <strong>128</strong>
          <span>魔力</span>
        </div>
      </section>

      <section className="combat-feed" aria-label="战斗日志">
        {combatLogs.map((log, index) => <p key={index}>{log}</p>)}
      </section>

      {bagOpen && (
        <section className="inventory-overlay" aria-label="背包界面">
          <section className="right-workbench">
            <section className="board-panel">
              <div className="board-grid">
                {state.board.cells.flat().map((cell) => (
                  <BoardCell
                    key={`${cell.row}-${cell.column}`}
                    cell={cell}
                    fullGem={cell.gem ? fullGemById.get(cell.gem.instance_id) ?? cell.gem : null}
                    hoveredGemId={hoveredGemId}
                    linkedGemIds={linkedGemIds}
                    onDropGem={dropGemOnCell}
                    onDragGem={beginDrag}
                    onPointerDragGem={beginPointerDrag}
                    onHoverGem={onGemHover}
                    onLeaveGem={() => {
                      setHoveredGemId(null);
                      setTooltip(null);
                    }}
                    onUnmountGem={unmountGem}
                  />
                ))}
              </div>
            </section>

            <section className="bag-panel">
              <div className="bag-grid">
                {state.inventory.filter((gem) => !gem.board_position).map((gem) => (
                  <button
                    key={gem.instance_id}
                    className={hoveredGemId === gem.instance_id ? "bag-cell hover-self" : "bag-cell"}
                    draggable
                    onDragStart={(event) => beginDrag(event, gem)}
                    onMouseDown={(event) => beginPointerDrag(event, gem)}
                    onMouseEnter={(event) => onGemHover(event, gem)}
                    onMouseMove={(event) => onGemHover(event, gem)}
                    onMouseLeave={() => {
                      setHoveredGemId(null);
                      setTooltip(null);
                    }}
                  >
                    <GemOrb gem={gem} />
                  </button>
                ))}
                {Array.from({ length: Math.max(0, 60 - state.inventory.filter((gem) => !gem.board_position).length) }).map((_, index) => (
                  <div key={`empty-${index}`} className="bag-empty-cell" />
                ))}
              </div>
            </section>
          </section>

          {tooltip && <GemTooltip tooltip={tooltip} />}
          {draggingGemId && <div className="drag-hint">拖到数独盘格子后松开</div>}
        </section>
      )}
    </main>
  );
}

function BoardCell({
  cell,
  fullGem,
  hoveredGemId,
  linkedGemIds,
  onDropGem,
  onDragGem,
  onPointerDragGem,
  onHoverGem,
  onLeaveGem,
  onUnmountGem
}: {
  cell: Cell;
  fullGem: Gem | null;
  hoveredGemId: string | null;
  linkedGemIds: Set<string>;
  onDropGem: (instanceId: string, row: number, column: number) => void;
  onDragGem: (event: DragEvent, gem: Gem) => void;
  onPointerDragGem: (event: MouseEvent, gem: Gem) => void;
  onHoverGem: (event: MouseEvent, gem: Gem) => void;
  onLeaveGem: () => void;
  onUnmountGem: (instanceId: string) => void;
}) {
  const gem = fullGem;
  const hoverClass = gem ? boardHoverClass(gem.instance_id, hoveredGemId, linkedGemIds) : "";
  return (
    <button
      className={`board-cell ${hoverClass}`}
      data-board-row={cell.row}
      data-board-column={cell.column}
      onDragOver={(event) => event.preventDefault()}
      onDrop={(event) => {
        event.preventDefault();
        const instanceId = event.dataTransfer.getData("text/plain");
        if (instanceId) onDropGem(instanceId, cell.row, cell.column);
      }}
      onDoubleClick={() => gem && onUnmountGem(gem.instance_id)}
    >
      {gem ? (
        <span
          draggable
          onDragStart={(event) => onDragGem(event, gem)}
          onMouseDown={(event) => onPointerDragGem(event, gem)}
          onMouseEnter={(event) => onHoverGem(event, gem)}
          onMouseMove={(event) => onHoverGem(event, gem)}
          onMouseLeave={onLeaveGem}
        >
          <GemOrb gem={gem} />
        </span>
      ) : null}
    </button>
  );
}

function useLinkedGemIds(state: AppState | null, hoveredGemId: string | null) {
  return useMemo(() => {
    const result = new Set<string>();
    if (!state || !hoveredGemId) return result;
    result.add(hoveredGemId);
    for (const entries of Object.values(state.board.highlights)) {
      for (const entry of entries) {
        if (entry.instance_ids.includes(hoveredGemId)) {
          for (const instanceId of entry.instance_ids) result.add(instanceId);
        }
      }
    }
    return result;
  }, [state, hoveredGemId]);
}

function boardHoverClass(instanceId: string, hoveredGemId: string | null, linkedGemIds: Set<string>) {
  if (!hoveredGemId) return "";
  if (instanceId === hoveredGemId) return "hover-self";
  if (linkedGemIds.has(instanceId)) return "hover-linked";
  return "hover-dim";
}

function MapTiles() {
  return (
    <>
      <div className="road road-main" />
      <div className="road road-cross" />
      <div className="arena" />
      {[
        [150, 80], [1240, 80], [180, 640], [1280, 610], [980, 180], [420, 190]
      ].map(([x, y], index) => <div key={index} className="house" style={{ left: x, top: y }} />)}
      {[
        [80, 90], [120, 135], [1380, 160], [1470, 220], [1120, 680], [220, 740]
      ].map(([x, y], index) => <div key={index} className="tree" style={{ left: x, top: y }} />)}
    </>
  );
}

function GemTooltip({ tooltip }: { tooltip: Tooltip }) {
  const { gem, x, y } = tooltip;
  const targets = (gem.current_effective_targets ?? []).map((target) => target.name_text).join("、") || "当前没有生效对象";
  return (
    <div className="gem-tooltip" style={{ left: Math.min(x + 18, window.innerWidth - 430), top: Math.min(y + 18, window.innerHeight - 360) }}>
      <div className="tooltip-title">
        <GemOrb gem={gem} />
        <div>
          <h3>{gem.name_text}</h3>
          <p>{gem.category_text}，{gem.rarity_text}，{gem.gem_type.display_text}</p>
        </div>
      </div>
      <p>{gem.gem_type.identity_text}</p>
      <div className="tag-list">{(gem.tags ?? []).map((tag) => <span key={tag.text}>{tag.text}</span>)}</div>
      <div className="tooltip-section">
        <strong>随机词缀</strong>
        {(gem.random_affixes ?? []).length === 0 ? <p>无</p> : gem.random_affixes.map((affix) => (
          <p key={`${affix.name_text}-${affix.stat.text}`}>{affix.gen_text} {affix.name_text}：{affix.stat.text} {affix.value}</p>
        ))}
      </div>
      <div className="tooltip-section">
        <strong>当前实际生效对象</strong>
        <p>{targets}</p>
      </div>
    </div>
  );
}

function GemOrb({ gem }: { gem: Gem }) {
  const className = gem.category_text.includes("主动") ? "active-orb" : "support-orb";
  return <span className={`gem-orb ${className}`}>{gem.name_text.slice(0, 1)}</span>;
}

function FireBoltView({ bolt }: { bolt: FireBolt }) {
  const length = Math.hypot(bolt.targetX - bolt.x, bolt.targetY - bolt.y);
  const angle = Math.atan2(bolt.targetY - bolt.y, bolt.targetX - bolt.x);
  return (
    <div
      className="fire-bolt"
      style={{
        left: bolt.x,
        top: bolt.y,
        width: length,
        opacity: Math.max(0, bolt.ttl / 0.42),
        transform: `rotate(${angle}rad)`
      }}
    />
  );
}

function createEnemy(id: number, playerX: number, playerY: number): Enemy {
  const angle = Math.random() * Math.PI * 2;
  const radius = 360 + Math.random() * 260;
  return {
    id,
    x: clamp(playerX + Math.cos(angle) * radius, 40, MAP_WIDTH - 40),
    y: clamp(playerY + Math.sin(angle) * radius, 40, MAP_HEIGHT - 40),
    hp: 32,
    maxHp: 32
  };
}

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}

function distance(a: { x: number; y: number }, b: { x: number; y: number }) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}
