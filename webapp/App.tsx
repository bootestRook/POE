import { DragEvent, MouseEvent, ReactNode, useEffect, useMemo, useRef, useState } from "react";

type Gem = {
  instance_id: string;
  item_kind?: "gem" | "ordinary";
  name_text: string;
  category_text: string;
  rarity_text: string;
  gem_type: { display_text: string; identity_text: string };
  tags: { id?: string; text: string }[];
  current_effective_targets: { name_text: string }[];
  board_position: { row: number; column: number } | null;
  tooltip_view?: TooltipView;
};

type TooltipView = {
  variant?: "active" | "support";
  icon_text: string;
  icon_color_key?: string;
  icon_sprite?: string;
  name_text: string;
  subtitle_text: string;
  type_identity_text: string;
  tags: TooltipTagView[];
  summary_lines?: TooltipRichLine[];
  sections: {
    description: { title_text: string; lines: string[] };
    stats: { title_text: string; lines: TooltipStatLine[] };
    random_affixes?: { title_text: string; lines: TooltipAffixLine[]; empty_text: string };
    recent_dps?: { title_text: string; lines: TooltipStatLine[] };
    bonuses?: { title_text: string; lines: string[] };
    base_skill_level?: { lines: string[] };
    conditions?: { rich_lines: TooltipRichLine[] };
    support_rules?: { rich_lines: TooltipRichLine[] };
    base_bonuses?: { rich_lines: TooltipRichLine[] };
    current_targets?: { title_text: string; lines: TooltipTargetLine[] };
    rules?: { title_text: string; lines: string[] };
  };
};

type TooltipTagView = {
  id?: string;
  text: string;
  tone?: string;
};

type TooltipStatLine = {
  label_text: string;
  value_text: string;
};

type TooltipAffixLine = {
  title_text: string;
  detail_text: string;
};

type TooltipTargetLine = {
  name_text: string;
  status_text: string;
};

type TooltipTextSegment = {
  text: string;
  tone?: string;
};

type TooltipRichLine = TooltipTextSegment[];

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
    source_instance_id: string;
    source_name_text: string;
    target_instance_id: string;
    stat: { text: string };
    value: number;
    relation_text: string;
    reason_text: string;
    applied: boolean;
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
  ui_text?: {
    only_gems_on_board?: string;
  };
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
  left: number;
  top: number;
  transform: string;
};

type FloatingOrigin =
  | { kind: "board"; row: number; column: number }
  | { kind: "bag"; slotIndex: number; instanceId: string };

type FloatingGem = {
  gem: Gem;
  origin: FloatingOrigin;
  x: number;
  y: number;
  offsetX: number;
  offsetY: number;
};

type DropTarget =
  | { kind: "board"; row: number; column: number }
  | { kind: "bag"; slotIndex: number }
  | { kind: "invalid" };

type PlacementResult =
  | { type: "place" }
  | { type: "swap"; nextFloatingItem: Gem; origin: FloatingOrigin }
  | { type: "reject"; reason?: "only_gems_on_board" };

type PlacementPrompt = {
  id: number;
  text: string;
  x: number;
  y: number;
};

type SupportPreview = {
  source: { row: number; column: number; instanceId: string };
  targets: { row: number; column: number; instanceId: string }[];
  color: string;
};

type SupportLine = {
  id: string;
  source: { row: number; column: number };
  target: { row: number; column: number };
  color: string;
};

type TileType = "ground" | "blocked" | "object";

type TilemapData = {
  mapId: string;
  width: number;
  height: number;
  tileSize: number;
  tiles: TileType[][];
  spawnPoint: {
    tileX: number;
    tileY: number;
    x: number;
    y: number;
  };
};

const TILE_RENDER_BY_TYPE: Record<TileType, { className: string }> = {
  ground: { className: "tile-ground" },
  blocked: { className: "tile-blocked" },
  object: { className: "tile-object-slot" }
};

const DEFAULT_TILEMAP = createDefaultTilemap(25, 15, 64);
const MAP_WIDTH = DEFAULT_TILEMAP.width * DEFAULT_TILEMAP.tileSize;
const MAP_HEIGHT = DEFAULT_TILEMAP.height * DEFAULT_TILEMAP.tileSize;
const PLAYER_SPEED = 250;
const FLOATING_GEM_OFFSET = { x: 18, y: 18 };
const INVENTORY_SLOT_COUNT = 60;
const INVENTORY_COLUMNS = 12;
const TOOLTIP_WIDTH = 410;
const TOOLTIP_SCREEN_PADDING = 8;

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
  const [player, setPlayer] = useState({ x: DEFAULT_TILEMAP.spawnPoint.x, y: DEFAULT_TILEMAP.spawnPoint.y, hp: 510, maxHp: 510 });
  const [enemies, setEnemies] = useState<Enemy[]>([]);
  const [texts, setTexts] = useState<FloatingText[]>([]);
  const [bolts, setBolts] = useState<FireBolt[]>([]);
  const [kills, setKills] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [combatLogs, setCombatLogs] = useState<string[]>([]);
  const [hoveredGemId, setHoveredGemId] = useState<string | null>(null);
  const [hoveredBoardCell, setHoveredBoardCell] = useState<string | null>(null);
  const [hoveredBagSlot, setHoveredBagSlot] = useState<number | null>(null);
  const [tooltip, setTooltip] = useState<Tooltip | null>(null);
  const [floatingGem, setFloatingGem] = useState<FloatingGem | null>(null);
  const [placementPrompt, setPlacementPrompt] = useState<PlacementPrompt | null>(null);
  const [showPersistentSupportLines, setShowPersistentSupportLines] = useState(true);
  const [inventorySlots, setInventorySlots] = useState<(string | null)[]>(() => Array(INVENTORY_SLOT_COUNT).fill(null));
  const keys = useRef(new Set<string>());
  const floatingGemRef = useRef<FloatingGem | null>(null);
  const lastFrame = useRef<number | null>(null);
  const nextEnemyId = useRef(1);
  const nextTextId = useRef(1);
  const nextBoltId = useRef(1);
  const nextPromptId = useRef(1);
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
    if (!state) return;
    setInventorySlots((current) => reconcileInventorySlots(current, state, floatingGemRef.current?.gem.instance_id ?? null));
  }, [state, floatingGem?.gem.instance_id]);

  useEffect(() => {
    floatingGemRef.current = floatingGem;
  }, [floatingGem]);

  useEffect(() => {
    function onMouseMove(event: globalThis.MouseEvent) {
      const current = floatingGemRef.current;
      if (!current) return;
      setFloatingGem({ ...current, x: event.clientX + current.offsetX, y: event.clientY + current.offsetY });
    }

    async function onMouseDown(event: globalThis.MouseEvent) {
      const current = floatingGemRef.current;
      if (!current) return;
      if (event.button !== 0) return;
      event.preventDefault();
      const element = document.elementFromPoint(event.clientX, event.clientY);
      const target = resolveDropTarget(element);
      const result = await placeFloatingItem(current, target, event);
      if (result.type === "place") {
        clearFloatingGem();
      } else if (result.type === "swap") {
        setFloatingItem(result.nextFloatingItem, result.origin, event.clientX, event.clientY, current.offsetX, current.offsetY);
      }
    }
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mousedown", onMouseDown);
    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mousedown", onMouseDown);
    };
  }, [state, inventorySlots]);

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

  async function placeFloatingItem(current: FloatingGem, target: DropTarget, event: globalThis.MouseEvent): Promise<PlacementResult> {
    if (target.kind === "invalid") return { type: "reject" };
    if (isDropBackToOrigin(current, target, state, inventorySlots)) return { type: "place" };
    if (target.kind === "bag") return await placeItemInBag(current, target.slotIndex);
    return await placeItemOnBoard(current, target.row, target.column, event);
  }

  async function placeItemInBag(current: FloatingGem, slotIndex: number): Promise<PlacementResult> {
    if (!state) return { type: "reject" };
    const instanceId = current.gem.instance_id;
    const dragged = inventoryItemById(state, instanceId);
    if (!dragged) {
      setNotice("没有找到这颗宝石。");
      return { type: "reject" };
    }
    const targetItem = inventoryItemById(state, inventorySlots[slotIndex]);
    if (!dragged.board_position) {
      setInventorySlots((slots) => moveItemToInventorySlot(slots, instanceId, slotIndex));
      return targetItem ? { type: "swap", nextFloatingItem: targetItem, origin: { kind: "bag", slotIndex, instanceId: targetItem.instance_id } } : { type: "place" };
    }

    try {
      const nextState = await requestState("/api/unmount", { instance_id: instanceId });
      setState(nextState);
      setInventorySlots((slots) => moveItemToInventorySlot(slots, instanceId, slotIndex));
      return targetItem ? { type: "swap", nextFloatingItem: targetItem, origin: { kind: "bag", slotIndex, instanceId: targetItem.instance_id } } : { type: "place" };
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "操作失败。");
      return { type: "reject" };
    }
  }

  async function placeItemOnBoard(current: FloatingGem, row: number, column: number, event: globalThis.MouseEvent): Promise<PlacementResult> {
    if (!state) return { type: "reject" };
    const instanceId = current.gem.instance_id;
    if (!isGemItem(current.gem)) {
      showPlacementPrompt(state.ui_text?.only_gems_on_board ?? "", event.clientX, event.clientY);
      return { type: "reject", reason: "only_gems_on_board" };
    }
    const target = state.board.cells[row]?.[column]?.gem;
    const targetItem = inventoryItemById(state, target?.instance_id);
    const dragged = inventoryItemById(state, instanceId);
    if (!dragged) {
      setNotice("没有找到这颗宝石。");
      return { type: "reject" };
    }
    if (dragged.board_position?.row === row && dragged.board_position.column === column) return { type: "place" };
    if (!canPlaceGemOnBoard(state, dragged, row, column, new Set([instanceId, targetItem?.instance_id ?? ""]))) return { type: "reject" };

    try {
      if (dragged.board_position) {
        await requestState("/api/unmount", { instance_id: instanceId });
      }
      if (targetItem) {
        await requestState("/api/unmount", { instance_id: targetItem.instance_id });
      }
      const nextState = await requestState("/api/mount", { instance_id: instanceId, row, column });
      setState(nextState);
      setInventorySlots((slots) => removeItemsFromInventorySlots(slots, [instanceId, targetItem?.instance_id ?? ""]));
      setNotice(`已将${dragged.name_text}放入第${row + 1}行第${column + 1}列。`);
      return targetItem ? { type: "swap", nextFloatingItem: targetItem, origin: { kind: "board", row, column } } : { type: "place" };
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "操作失败。");
      return { type: "reject" };
    }
  }

  async function dropGemOnCell(instanceId: string, row: number, column: number): Promise<boolean> {
    const item = state ? inventoryItemById(state, instanceId) : null;
    if (!item) return false;
    const result = await placeItemOnBoard(
      { gem: item, origin: { kind: "board", row, column }, x: 0, y: 0, offsetX: FLOATING_GEM_OFFSET.x, offsetY: FLOATING_GEM_OFFSET.y },
      row,
      column,
      { clientX: 0, clientY: 0 } as globalThis.MouseEvent
    );
    return result.type !== "reject";
  }

  function clearFloatingGem() {
    floatingGemRef.current = null;
    setFloatingGem(null);
  }

  function setFloatingItem(item: Gem, origin: FloatingOrigin, x: number, y: number, offsetX = FLOATING_GEM_OFFSET.x, offsetY = FLOATING_GEM_OFFSET.y) {
    const nextFloatingGem: FloatingGem = {
      gem: item,
      origin,
      x: x + offsetX,
      y: y + offsetY,
      offsetX,
      offsetY
    };
    floatingGemRef.current = nextFloatingGem;
    setFloatingGem(nextFloatingGem);
  }

  function showPlacementPrompt(text: string, x: number, y: number) {
    const id = nextPromptId.current++;
    setPlacementPrompt({ id, text, x, y });
    window.setTimeout(() => {
      setPlacementPrompt((current) => (current?.id === id ? null : current));
    }, 900);
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

  function beginDrag(event: DragEvent) {
    event.preventDefault();
  }

  function beginPointerDrag(event: MouseEvent, gem: Gem, origin: FloatingOrigin) {
    if (event.button !== 0) return;
    if (floatingGemRef.current) return;
    event.preventDefault();
    event.stopPropagation();
    setTooltip(null);
    setHoveredGemId(null);
    setFloatingItem(gem, origin, event.clientX, event.clientY);
  }

  function onGemHover(event: MouseEvent, gem: Gem, source: "board" | "inventory", slotIndex?: number) {
    setHoveredGemId(gem.instance_id);
    setTooltip({ gem, ...resolveTooltipPosition(event.currentTarget as HTMLElement, source, slotIndex) });
  }

  const linkedGemIds = useLinkedGemIds(state, hoveredGemId);
  const fullGemById = useMemo(() => {
    const result = new Map<string, Gem>();
    for (const gem of state?.inventory ?? []) result.set(gem.instance_id, gem);
    return result;
  }, [state]);
  const hoveredBoardGemId = hoveredGemId && fullGemById.get(hoveredGemId)?.board_position ? hoveredGemId : null;
  const legalDropCells = useLegalDropCells(state, floatingGem && isGemItem(floatingGem.gem) ? floatingGem.gem : null);
  const supportPreview = useSupportPreview(state, fullGemById, hoveredGemId, floatingGem);
  const persistentSupportLines = useSupportLines(state, fullGemById);
  const activeTargetLines = useActiveTargetLines(persistentSupportLines, fullGemById, hoveredGemId, floatingGem);
  const bagSlots = inventorySlots.map((instanceId) => (instanceId ? fullGemById.get(instanceId) ?? null : null));

  if (!state) return <main className="game-screen loading">{notice}</main>;

  return (
    <main className="game-screen">
      <section className="map-layer" aria-label="可玩地图">
        <div
          className="terrain"
          style={{
            width: MAP_WIDTH,
            height: MAP_HEIGHT,
            transform: `translate(calc(50vw - ${player.x}px), calc(50vh - ${player.y}px))`
          }}
        >
          <MapTiles tilemap={DEFAULT_TILEMAP} />
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
                    hoveredGemId={hoveredBoardGemId}
                    linkedGemIds={linkedGemIds}
                    supportPreview={supportPreview}
                    floatingGemId={floatingGem?.gem.instance_id ?? null}
                    legalDropCells={legalDropCells}
                    hoveredBoardCell={hoveredBoardCell}
                    onHoverCell={setHoveredBoardCell}
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
                {supportPreview
                  ? supportPreview.targets.length > 0 && <SupportPreviewLines preview={supportPreview} />
                  : activeTargetLines
                    ? activeTargetLines.length > 0 && <SupportLines lines={activeTargetLines} className="support-hover-lines" />
                  : showPersistentSupportLines && persistentSupportLines.length > 0 && <SupportLines lines={persistentSupportLines} />}
              </div>
              <label className="support-line-toggle">
                <input
                  type="checkbox"
                  checked={showPersistentSupportLines}
                  onChange={(event) => setShowPersistentSupportLines(event.currentTarget.checked)}
                />
                <span>常驻显示连线</span>
              </label>
            </section>

            <section className="bag-panel">
              <div className="bag-grid" data-bag-drop-target="true">
                {bagSlots.map((gem, slotIndex) => (
                  gem ? (
                    <button
                      key={`bag-${slotIndex}`}
                      className={bagCellClass(slotIndex, hoveredBagSlot, gem, hoveredGemId, floatingGem)}
                      data-bag-drop-target="true"
                      data-bag-slot-index={slotIndex}
                      draggable={false}
                      onDragStart={beginDrag}
                      onMouseDown={(event) => beginPointerDrag(event, gem, { kind: "bag", slotIndex, instanceId: gem.instance_id })}
                      onMouseEnter={(event) => {
                        setHoveredBagSlot(slotIndex);
                        onGemHover(event, gem, "inventory", slotIndex);
                      }}
                      onMouseMove={(event) => onGemHover(event, gem, "inventory", slotIndex)}
                      onMouseLeave={() => {
                        setHoveredBagSlot(null);
                        setHoveredGemId(null);
                        setTooltip(null);
                      }}
                    >
                      {isFloatingOrigin(floatingGem, { kind: "bag", slotIndex, instanceId: gem.instance_id }) ? <GemGhost /> : <GemOrb gem={gem} />}
                    </button>
                  ) : (
                    <div
                      key={`bag-${slotIndex}`}
                      className={bagEmptyCellClass(slotIndex, hoveredBagSlot)}
                      data-bag-drop-target="true"
                      data-bag-slot-index={slotIndex}
                      onMouseEnter={() => setHoveredBagSlot(slotIndex)}
                      onMouseLeave={() => setHoveredBagSlot(null)}
                    />
                  )
                ))}
              </div>
            </section>
          </section>

          {tooltip && !floatingGem && <GemTooltip tooltip={tooltip} />}
          {floatingGem && <FloatingGemView floatingGem={floatingGem} />}
          {floatingGem && <div className="drag-hint">拖到数独盘格子后松开</div>}
          {placementPrompt && (
            <div className="placement-prompt" style={{ left: placementPrompt.x, top: placementPrompt.y }}>
              {placementPrompt.text}
            </div>
          )}
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
  supportPreview,
  floatingGemId,
  legalDropCells,
  hoveredBoardCell,
  onHoverCell,
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
  supportPreview: SupportPreview | null;
  floatingGemId: string | null;
  legalDropCells: Set<string>;
  hoveredBoardCell: string | null;
  onHoverCell: (cellKey: string | null) => void;
  onDropGem: (instanceId: string, row: number, column: number) => Promise<boolean>;
  onDragGem: (event: DragEvent) => void;
  onPointerDragGem: (event: MouseEvent, gem: Gem, origin: FloatingOrigin) => void;
  onHoverGem: (event: MouseEvent, gem: Gem, source: "board" | "inventory", slotIndex?: number) => void;
  onLeaveGem: () => void;
  onUnmountGem: (instanceId: string) => void;
}) {
  const gem = fullGem;
  const origin: FloatingOrigin = { kind: "board", row: cell.row, column: cell.column };
  const isGhost = Boolean(gem && floatingGemId === gem.instance_id);
  const previewClass = supportPreview ? boardSupportPreviewClass(cell, supportPreview) : "";
  const hoverClass = previewClass || (gem ? boardHoverClass(gem.instance_id, hoveredGemId, linkedGemIds) : "");
  const legalClass = legalDropCells.has(cellKey(cell.row, cell.column)) ? "legal-drop-cell" : "";
  const currentCellKey = cellKey(cell.row, cell.column);
  const boardHoverClassName = hoveredBoardCell === currentCellKey ? "board-slot-hover" : "";
  return (
    <button
      className={`board-cell ${hoverClass} ${legalClass} ${boardHoverClassName}`}
      data-board-row={cell.row}
      data-board-column={cell.column}
      onMouseEnter={() => onHoverCell(currentCellKey)}
      onMouseLeave={() => onHoverCell(null)}
      onDragOver={(event) => event.preventDefault()}
      onDrop={(event) => {
        event.preventDefault();
        const instanceId = event.dataTransfer.getData("text/plain");
        if (instanceId) onDropGem(instanceId, cell.row, cell.column);
      }}
      onDoubleClick={() => gem && !isGhost && onUnmountGem(gem.instance_id)}
    >
      {gem && !isGhost ? (
        <span
          draggable={false}
          onDragStart={onDragGem}
          onMouseDown={(event) => onPointerDragGem(event, gem, origin)}
          onMouseEnter={(event) => onHoverGem(event, gem, "board")}
          onMouseMove={(event) => onHoverGem(event, gem, "board")}
          onMouseLeave={onLeaveGem}
        >
          <GemOrb gem={gem} />
        </span>
      ) : isGhost ? (
        <GemGhost />
      ) : null}
    </button>
  );
}

function FloatingGemView({ floatingGem }: { floatingGem: FloatingGem }) {
  return (
    <div className="floating-gem" style={{ left: floatingGem.x, top: floatingGem.y }}>
      <GemOrb gem={floatingGem.gem} />
    </div>
  );
}

function GemGhost() {
  return <span className="gem-ghost" />;
}

function SupportPreviewLines({ preview }: { preview: SupportPreview }) {
  return (
    <SupportLines
      className="support-hover-lines"
      lines={preview.targets.map((target) => ({
        id: target.instanceId,
        source: preview.source,
        target,
        color: preview.color
      }))}
    />
  );
}

function SupportLines({ lines, className = "" }: { lines: SupportLine[]; className?: string }) {
  return (
    <svg className={`support-preview-lines ${className}`} viewBox="0 0 9 9" aria-hidden="true">
      {lines.map((line) => (
        <line
          key={line.id}
          x1={line.source.column + 0.5}
          y1={line.source.row + 0.5}
          x2={line.target.column + 0.5}
          y2={line.target.row + 0.5}
          style={{ stroke: line.color }}
        />
      ))}
    </svg>
  );
}

function useLegalDropCells(state: AppState | null, floatingGem: Gem | null) {
  return useMemo(() => {
    const result = new Set<string>();
    if (!state || !floatingGem) return result;

    const floatingGemType = gemTypeKey(floatingGem);
    for (const row of state.board.cells) {
      for (const cell of row) {
        const target = cell.gem;
        const ignoredInstanceIds = new Set([floatingGem.instance_id, target?.instance_id ?? ""]);

        const hasConflict = state.board.cells.some((otherRow) =>
          otherRow.some((otherCell) => {
            const otherGem = otherCell.gem;
            if (!otherGem || ignoredInstanceIds.has(otherGem.instance_id)) return false;
            if (gemTypeKey(otherGem) !== floatingGemType) return false;
            return otherCell.row === cell.row || otherCell.column === cell.column || otherCell.box === cell.box;
          })
        );
        if (!hasConflict) result.add(cellKey(cell.row, cell.column));
      }
    }

    return result;
  }, [state, floatingGem]);
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

function useSupportPreview(state: AppState | null, fullGemById: Map<string, Gem>, hoveredGemId: string | null, floatingGem: FloatingGem | null) {
  return useMemo<SupportPreview | null>(() => {
    if (!state || !hoveredGemId || floatingGem) return null;
    const sourceGem = fullGemById.get(hoveredGemId);
    if (!sourceGem || !sourceGem.board_position || !isSupportGem(sourceGem)) return null;

    const targetIds = new Set<string>();
    for (const skill of state.skill_preview) {
      for (const modifier of skill.applied_modifiers) {
        if (modifier.applied && modifier.source_instance_id === sourceGem.instance_id && modifier.target_instance_id) {
          targetIds.add(modifier.target_instance_id);
        }
      }
    }

    const targets = state.board.cells.flat()
      .map((cell) => {
        if (!cell.gem || !targetIds.has(cell.gem.instance_id)) return null;
        const gem = fullGemById.get(cell.gem.instance_id) ?? cell.gem;
        if (!isActiveGem(gem)) return null;
        return { row: cell.row, column: cell.column, instanceId: gem.instance_id };
      })
      .filter((target): target is { row: number; column: number; instanceId: string } => Boolean(target));

    return {
      source: {
        row: sourceGem.board_position.row,
        column: sourceGem.board_position.column,
        instanceId: sourceGem.instance_id
      },
      targets,
      color: gemColorValue(sourceGem)
    };
  }, [state, fullGemById, hoveredGemId, floatingGem]);
}

function useSupportLines(state: AppState | null, fullGemById: Map<string, Gem>) {
  return useMemo<SupportLine[]>(() => {
    if (!state) return [];
    const result = new Map<string, SupportLine>();
    for (const skill of state.skill_preview) {
      for (const modifier of skill.applied_modifiers) {
        if (!modifier.applied || !modifier.source_instance_id || !modifier.target_instance_id) continue;
        const sourceGem = fullGemById.get(modifier.source_instance_id);
        const targetGem = fullGemById.get(modifier.target_instance_id);
        if (!sourceGem?.board_position || !targetGem?.board_position) continue;
        if (!isSupportGem(sourceGem) || !isActiveGem(targetGem)) continue;
        const key = `${sourceGem.instance_id}-${targetGem.instance_id}`;
        if (result.has(key)) continue;
        result.set(key, {
          id: key,
          source: sourceGem.board_position,
          target: targetGem.board_position,
          color: gemColorValue(sourceGem)
        });
      }
    }
    return [...result.values()];
  }, [state, fullGemById]);
}

function useActiveTargetLines(lines: SupportLine[], fullGemById: Map<string, Gem>, hoveredGemId: string | null, floatingGem: FloatingGem | null) {
  return useMemo<SupportLine[] | null>(() => {
    if (!hoveredGemId || floatingGem) return null;
    const hoveredGem = fullGemById.get(hoveredGemId);
    if (!hoveredGem?.board_position || !isActiveGem(hoveredGem)) return null;
    return lines.filter((line) => line.target.row === hoveredGem.board_position?.row && line.target.column === hoveredGem.board_position.column);
  }, [lines, fullGemById, hoveredGemId, floatingGem]);
}

function boardHoverClass(instanceId: string, hoveredGemId: string | null, linkedGemIds: Set<string>) {
  if (!hoveredGemId) return "";
  if (instanceId === hoveredGemId) return "hover-self";
  if (linkedGemIds.has(instanceId)) return "hover-linked";
  return "hover-dim";
}

function boardSupportPreviewClass(cell: Cell, preview: SupportPreview) {
  const instanceId = cell.gem?.instance_id ?? "";
  if (instanceId === preview.source.instanceId) return "support-preview-source";
  if (preview.targets.some((target) => target.instanceId === instanceId)) return "support-preview-target";
  return "support-preview-dim";
}

function bagCellClass(slotIndex: number, hoveredBagSlot: number | null, gem: Gem, hoveredGemId: string | null, floatingGem: FloatingGem | null) {
  const classes = ["bag-cell"];
  if (hoveredBagSlot === slotIndex) classes.push("bag-slot-hover");
  if (hoveredGemId === gem.instance_id) classes.push("hover-self");
  if (isFloatingOrigin(floatingGem, { kind: "bag", slotIndex, instanceId: gem.instance_id })) classes.push("has-ghost");
  return classes.join(" ");
}

function bagEmptyCellClass(slotIndex: number, hoveredBagSlot: number | null) {
  const classes = ["bag-empty-cell"];
  if (hoveredBagSlot === slotIndex) classes.push("bag-slot-hover");
  return classes.join(" ");
}

function resolveTooltipPosition(anchor: HTMLElement, source: "board" | "inventory", slotIndex?: number): Omit<Tooltip, "gem"> {
  if (source === "board") return getBoardTooltipPosition(anchor);
  return getInventoryTooltipPosition(anchor, slotIndex ?? 0);
}

function getBoardTooltipPosition(anchor: HTMLElement): Omit<Tooltip, "gem"> {
  const cell = anchor.closest("[data-board-row][data-board-column]") as HTMLElement | null;
  const board = anchor.closest(".board-grid") as HTMLElement | null;
  const cellRect = (cell ?? anchor).getBoundingClientRect();
  const boardRect = (board ?? anchor).getBoundingClientRect();
  const centerTop = clampTooltipTop(cellRect.top + cellRect.height / 2);

  return {
    left: clampTooltipLeft(boardRect.left - 5 - TOOLTIP_WIDTH),
    top: centerTop,
    transform: `translateY(max(-50%, ${boardRect.top - centerTop}px))`
  };
}

function getInventoryTooltipPosition(anchor: HTMLElement, slotIndex: number): Omit<Tooltip, "gem"> {
  const rect = anchor.getBoundingClientRect();
  const columnIndex = slotIndex % INVENTORY_COLUMNS;
  if (columnIndex >= INVENTORY_COLUMNS - 4) {
    return {
      left: clampTooltipLeft(rect.left - 2 - TOOLTIP_WIDTH),
      top: clampTooltipTop(rect.top + rect.height / 2),
      transform: "translateY(-50%)"
    };
  }

  return {
    left: clampTooltipLeft(rect.left + rect.width / 2 - TOOLTIP_WIDTH / 2),
    top: Math.max(TOOLTIP_SCREEN_PADDING, rect.top - 2),
    transform: "translateY(-100%)"
  };
}

function clampTooltipLeft(left: number) {
  return Math.max(TOOLTIP_SCREEN_PADDING, Math.min(left, window.innerWidth - TOOLTIP_WIDTH - TOOLTIP_SCREEN_PADDING));
}

function clampTooltipTop(top: number) {
  return Math.max(TOOLTIP_SCREEN_PADDING, Math.min(top, window.innerHeight - TOOLTIP_SCREEN_PADDING));
}

function isFloatingOrigin(floatingGem: FloatingGem | null, origin: FloatingOrigin) {
  if (!floatingGem) return false;
  const current = floatingGem.origin;
  if (current.kind !== origin.kind) return false;
  if (current.kind === "bag" && origin.kind === "bag") return current.slotIndex === origin.slotIndex && current.instanceId === origin.instanceId;
  if (current.kind === "board" && origin.kind === "board") return current.row === origin.row && current.column === origin.column;
  return false;
}

function resolveDropTarget(element: Element | null): DropTarget {
  const boardCell = element?.closest("[data-board-row][data-board-column]") as HTMLElement | null;
  if (boardCell) {
    return {
      kind: "board",
      row: Number(boardCell.dataset.boardRow),
      column: Number(boardCell.dataset.boardColumn)
    };
  }

  const bagCell = element?.closest("[data-bag-slot-index]") as HTMLElement | null;
  if (bagCell) return { kind: "bag", slotIndex: Number(bagCell.dataset.bagSlotIndex) };
  return { kind: "invalid" };
}

function isDropBackToOrigin(floatingGem: FloatingGem, target: DropTarget, state: AppState | null, inventorySlots: (string | null)[]) {
  const origin = floatingGem.origin;
  if (origin.kind === "bag") {
    return target.kind === "bag" && origin.slotIndex === target.slotIndex && inventorySlots[target.slotIndex] === floatingGem.gem.instance_id;
  }
  return (
    target.kind === "board" &&
    origin.row === target.row &&
    origin.column === target.column &&
    state?.board.cells[target.row]?.[target.column]?.gem?.instance_id === floatingGem.gem.instance_id
  );
}

function reconcileInventorySlots(current: (string | null)[], state: AppState, floatingItemId: string | null) {
  const unmountedIds = new Set(state.inventory.filter((gem) => !gem.board_position).map((gem) => gem.instance_id));
  const next = Array(INVENTORY_SLOT_COUNT).fill(null) as (string | null)[];
  const used = new Set<string>();

  current.slice(0, INVENTORY_SLOT_COUNT).forEach((instanceId, index) => {
    if (instanceId && instanceId !== floatingItemId && unmountedIds.has(instanceId) && !used.has(instanceId)) {
      next[index] = instanceId;
      used.add(instanceId);
    }
  });

  for (const gem of state.inventory) {
    if (gem.board_position || gem.instance_id === floatingItemId || used.has(gem.instance_id)) continue;
    const emptyIndex = next.findIndex((instanceId) => instanceId === null);
    if (emptyIndex >= 0) {
      next[emptyIndex] = gem.instance_id;
      used.add(gem.instance_id);
    }
  }

  return next;
}

function moveItemToInventorySlot(slots: (string | null)[], instanceId: string, slotIndex: number) {
  const next = slots.slice(0, INVENTORY_SLOT_COUNT);
  while (next.length < INVENTORY_SLOT_COUNT) next.push(null);
  for (let index = 0; index < next.length; index += 1) {
    if (next[index] === instanceId) next[index] = null;
  }
  next[slotIndex] = instanceId;
  return next;
}

function removeItemsFromInventorySlots(slots: (string | null)[], instanceIds: string[]) {
  const idSet = new Set(instanceIds.filter(Boolean));
  return slots.map((slotInstanceId) => (slotInstanceId && idSet.has(slotInstanceId) ? null : slotInstanceId));
}

function canPlaceGemOnBoard(state: AppState, gem: Gem, row: number, column: number, ignoredInstanceIds = new Set<string>()) {
  const target = state.board.cells[row]?.[column];
  if (!target) return false;
  if (target.gem && target.gem.instance_id !== gem.instance_id && !ignoredInstanceIds.has(target.gem.instance_id)) return false;

  const gemType = gemTypeKey(gem);
  return !state.board.cells.some((boardRow) =>
    boardRow.some((cell) => {
      const otherGem = cell.gem;
      if (!otherGem || otherGem.instance_id === gem.instance_id || ignoredInstanceIds.has(otherGem.instance_id)) return false;
      if (gemTypeKey(otherGem) !== gemType) return false;
      return cell.row === row || cell.column === column || cell.box === target.box;
    })
  );
}

function inventoryItemById(state: AppState, instanceId: string | null | undefined) {
  if (!instanceId) return null;
  return state.inventory.find((item) => item.instance_id === instanceId) ?? null;
}

function isGemItem(item: Gem) {
  return item.item_kind !== "ordinary" && item.tags.some((tag) => tag.id === "gem");
}

function isActiveGem(item: Gem) {
  return item.tags.some((tag) => tag.id === "active_skill_gem");
}

function isSupportGem(item: Gem) {
  return item.tags.some((tag) => tag.id === "support_gem");
}

function cellKey(row: number, column: number) {
  return `${row}-${column}`;
}

function gemTypeKey(gem: Gem) {
  return gem.gem_type.identity_text || gem.gem_type.display_text;
}

function createDefaultTilemap(width: number, height: number, tileSize: number): TilemapData {
  const spawnTileX = Math.floor(width / 2);
  const spawnTileY = Math.floor(height / 2);
  const tiles: TileType[][] = Array.from({ length: height }, (_, y) =>
    Array.from({ length: width }, (_, x) => (x === 0 || y === 0 || x === width - 1 || y === height - 1 ? "blocked" : "ground"))
  );

  return {
    mapId: "v1-clean-tilemap",
    width,
    height,
    tileSize,
    tiles,
    spawnPoint: {
      tileX: spawnTileX,
      tileY: spawnTileY,
      x: spawnTileX * tileSize + tileSize / 2,
      y: spawnTileY * tileSize + tileSize / 2
    }
  };
}

function MapTiles({ tilemap }: { tilemap: TilemapData }) {
  return (
    <>
      {tilemap.tiles.flatMap((row, y) =>
        row.map((tile, x) => (
          <div
            key={`${x}-${y}`}
            className={`map-tile ${TILE_RENDER_BY_TYPE[tile].className}`}
            data-tile-type={tile}
            style={{
              left: x * tilemap.tileSize,
              top: y * tilemap.tileSize,
              width: tilemap.tileSize,
              height: tilemap.tileSize
            }}
          />
        ))
      )}
    </>
  );
}

function GemTooltip({ tooltip }: { tooltip: Tooltip }) {
  const { gem, left, top, transform } = tooltip;
  const view = buildGemTooltipViewModel(gem);
  if (!view) return null;
  if (view.variant === "support") {
    return <SupportGemTooltip gem={gem} view={view} left={left} top={top} transform={transform} />;
  }
  const isActiveTooltip = view.variant === "active";
  const sections = view.sections;
  return (
    <div className={`gem-tooltip ${isActiveTooltip ? "active-tooltip" : ""}`} style={{ left, top, transform }}>
      <div className="tooltip-header">
        <GemOrb gem={gem} />
        <div className="tooltip-heading">
          <h3 className={isActiveTooltip ? "tooltip-tone-title" : undefined}>{view.name_text}</h3>
          {isActiveTooltip ? <RichText line={highlightTooltipText(view.subtitle_text)} /> : <p>{view.subtitle_text}</p>}
        </div>
      </div>
      {view.type_identity_text && <p className="tooltip-identity">{view.type_identity_text}</p>}
      {!isActiveTooltip && <div className="tooltip-tag-list">{view.tags.map((tag) => <TooltipTag key={`${tag.id ?? tag.text}-${tag.text}`} tag={tag} />)}</div>}
      <TooltipSection title={sections.description.title_text}>
        {sections.description.lines.map((line) => isActiveTooltip ? <RichText key={line} line={highlightTooltipText(line)} /> : <p key={line}>{line}</p>)}
      </TooltipSection>
      {sections.stats.lines.length > 0 && <TooltipSection title={sections.stats.title_text}>
        <dl className="tooltip-stat-list">
          {sections.stats.lines.map((line) => (
            <div key={`${line.label_text}-${line.value_text}`} className="tooltip-stat-line">
              <dt className={isActiveTooltip ? "tooltip-tone-body" : undefined}>{line.label_text}：</dt>
              <dd className={isActiveTooltip ? "tooltip-tone-body" : undefined}>{line.value_text}</dd>
            </div>
          ))}
        </dl>
      </TooltipSection>}
      {sections.recent_dps && sections.recent_dps.lines.length > 0 && (
        <TooltipSection title={sections.recent_dps.title_text}>
          <dl className="tooltip-stat-list">
            {sections.recent_dps.lines.map((line) => (
              <div key={`${line.label_text}-${line.value_text}`} className="tooltip-stat-line">
                <dt className={isActiveTooltip ? "tooltip-tone-body" : undefined}>{line.label_text}：</dt>
                <dd className={isActiveTooltip ? activeDpsToneClass(line.value_text) : undefined}>{line.value_text}</dd>
              </div>
            ))}
          </dl>
        </TooltipSection>
      )}
      {sections.bonuses && sections.bonuses.lines.length > 0 && (
        <TooltipSection title={sections.bonuses.title_text}>
          {sections.bonuses.lines.map((line, index) => <p key={`${index}-${line}`} className={`tooltip-bonus-line ${isActiveTooltip ? "tooltip-tone-rule" : ""}`}>{line}</p>)}
        </TooltipSection>
      )}
      {isActiveTooltip && sections.base_skill_level && sections.base_skill_level.lines.length > 0 && (
        <TooltipSection title="">
          {sections.base_skill_level.lines.map((line) => <p key={line} className="tooltip-tone-bonus-positive">{line}</p>)}
        </TooltipSection>
      )}
      {sections.random_affixes && sections.random_affixes.lines.length > 0 && (
        <TooltipSection title={sections.random_affixes.title_text}>
          {sections.random_affixes.lines.map((line) => (
            <p key={`${line.title_text}-${line.detail_text}`} className="tooltip-affix-line">
              <span>{line.title_text}</span>
              <strong>{line.detail_text}</strong>
            </p>
          ))}
        </TooltipSection>
      )}
      {sections.current_targets && sections.current_targets.lines.length > 0 && <TooltipSection title={sections.current_targets.title_text}>
        {sections.current_targets.lines.map((line) => (
          <p key={`${line.name_text}-${line.status_text}`} className="tooltip-target-line">
            <span>{line.name_text}</span>
            <strong>{line.status_text}</strong>
          </p>
        ))}
      </TooltipSection>}
      {sections.rules && sections.rules.lines.length > 0 && <TooltipSection title={sections.rules.title_text}>
        {sections.rules.lines.map((line) => <p key={line} className={isActiveTooltip ? "tooltip-tone-bonus-positive" : undefined}>{line}</p>)}
      </TooltipSection>}
    </div>
  );
}

function SupportGemTooltip({ gem, view, left, top, transform }: { gem: Gem; view: TooltipView; left: number; top: number; transform: string }) {
  const sections = view.sections;
  return (
    <div className="gem-tooltip support-tooltip" style={{ left, top, transform }}>
      <div className="tooltip-header">
        <GemOrb gem={gem} />
        <div className="tooltip-heading">
          <h3 className="support-tooltip-name">{view.name_text}</h3>
          {(view.summary_lines ?? []).map((line, index) => <RichText key={index} line={line} className="support-tooltip-summary" />)}
        </div>
      </div>
      <TooltipSection title={sections.description.title_text}>
        {(sections.description as { rich_lines?: TooltipRichLine[] }).rich_lines?.map((line, index) => <RichText key={index} line={line} />)}
      </TooltipSection>
      {sections.conditions && sections.conditions.rich_lines.length > 0 && (
        <TooltipSection title="">
          {sections.conditions.rich_lines.map((line, index) => <RichText key={index} line={line} />)}
        </TooltipSection>
      )}
      {sections.support_rules && sections.support_rules.rich_lines.length > 0 && (
        <TooltipSection title="">
          {sections.support_rules.rich_lines.map((line, index) => <RichText key={index} line={line} />)}
        </TooltipSection>
      )}
      {sections.base_bonuses && sections.base_bonuses.rich_lines.length > 0 && (
        <TooltipSection title="">
          {sections.base_bonuses.rich_lines.map((line, index) => <RichText key={index} line={line} />)}
        </TooltipSection>
      )}
    </div>
  );
}

function RichText({ line, className = "" }: { line: TooltipRichLine; className?: string }) {
  return (
    <p className={`tooltip-rich-line ${className}`}>
      {line.map((segment, index) => (
        <span key={`${index}-${segment.text}`} className={segment.tone ? `tooltip-tone-${segment.tone}` : undefined}>
          {segment.text}
        </span>
      ))}
    </p>
  );
}

const tooltipHighlightTones: Record<string, string> = {
  "红色": "color-red",
  "蓝色": "color-blue",
  "绿色": "color-green",
  "粉色": "color-pink",
  "黄色": "color-yellow",
  "白色": "color-white",
  "黑色": "color-black",
  "青色": "color-cyan",
  "橙色": "color-orange",
  "火焰": "damage-fire",
  "冰霜": "damage-cold",
  "闪电": "damage-lightning",
  "物理": "damage-physical",
  "混沌": "damage-chaos"
};

const tooltipHighlightTerms = Object.keys(tooltipHighlightTones).sort((left, right) => right.length - left.length);

function highlightTooltipText(text: string): TooltipRichLine {
  const segments: TooltipRichLine = [];
  let index = 0;
  while (index < text.length) {
    const term = tooltipHighlightTerms.find((candidate) => text.startsWith(candidate, index));
    if (term) {
      segments.push({ text: term, tone: tooltipHighlightTones[term] });
      index += term.length;
      continue;
    }
    const nextIndex = tooltipHighlightTerms.reduce((next, candidate) => {
      const found = text.indexOf(candidate, index + 1);
      return found >= 0 ? Math.min(next, found) : next;
    }, text.length);
    segments.push({ text: text.slice(index, nextIndex), tone: "body" });
    index = nextIndex;
  }
  return segments;
}

function activeDpsToneClass(valueText: string) {
  if (valueText.includes("↘") || valueText.includes("-")) {
    return "tooltip-tone-color-red";
  }
  if (valueText.includes("↗") || valueText.includes("+")) {
    return "tooltip-tone-color-green";
  }
  return "tooltip-tone-body";
}

function buildGemTooltipViewModel(gem: Gem) {
  return gem.tooltip_view;
}

function TooltipTag({ tag }: { tag: TooltipTagView }) {
  return <span className={`tooltip-tag ${tag.tone ? `tooltip-tag-${tag.tone}` : ""}`}>{tag.text}</span>;
}

function TooltipSection({ children }: { title: string; children: ReactNode }) {
  return (
    <section className="tooltip-section">
      <div className="tooltip-section-content">{children}</div>
    </section>
  );
}

function GemOrb({ gem }: { gem: Gem }) {
  const sprite = gem.tooltip_view?.icon_sprite;
  const className = !isGemItem(gem)
    ? "item-orb"
    : `gem-orb-color-${gem.tooltip_view?.icon_color_key ?? gemColorKey(gem)}`;
  const style = sprite ? ({ "--gem-icon-sprite": `url(${sprite})` } as React.CSSProperties) : undefined;
  return (
    <span className={`gem-orb ${className} ${sprite ? "gem-orb-sprite" : ""}`} style={style}>
      {sprite ? <span className="gem-orb-label">{gem.tooltip_view?.icon_text ?? gem.name_text.slice(0, 1)}</span> : gem.tooltip_view?.icon_text ?? gem.name_text.slice(0, 1)}
    </span>
  );
}

function gemColorKey(gem: Gem) {
  const gemType = gem.gem_type?.id ?? gem.tags.find((tag) => tag.id?.startsWith("gem_type_"))?.id ?? "";
  const number = Number(gemType.split("_").pop());
  const colorByType: Record<number, string> = {
    1: "red",
    2: "blue",
    3: "green",
    4: "pink",
    5: "yellow",
    6: "white",
    7: "black",
    8: "cyan",
    9: "orange"
  };
  return colorByType[number] ?? "white";
}

function gemColorValue(gem: Gem) {
  const colors: Record<string, string> = {
    red: "#FF4D4D",
    blue: "#4DA3FF",
    green: "#5CDB7A",
    pink: "#FF5FD2",
    yellow: "#FFD84D",
    white: "#D8D8D8",
    black: "#B08CFF",
    cyan: "#4DDFFF",
    orange: "#FF9A3D"
  };
  return colors[gem.tooltip_view?.icon_color_key ?? gemColorKey(gem)] ?? "#A8A6FF";
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
