## 1. Encounter Data Model

- [x] 1.1 Extend map editor monster spawn and boss group types with optional aggro range fields.
- [x] 1.2 Extend monster spawn types with random count multiplier minimum and maximum fields.
- [x] 1.3 Update normalization so existing maps load with default aggro ranges and `[1, 1]` count multipliers.
- [x] 1.4 Ensure create-new, reset, load, local auto-save, file save, and whole-map shift flows preserve the new encounter fields.

## 2. Map Editor Authoring UI

- [x] 2.1 Add selected monster spawn controls for aggro range, count multiplier minimum, and count multiplier maximum.
- [x] 2.2 Add selected boss group controls for aggro range.
- [x] 2.3 Render visually distinct spawn-radius and aggro-radius rings for monster spawn points and boss groups.
- [x] 2.4 Add pointer interaction for adjusting aggro range without changing spawn radius or point center.
- [x] 2.5 Add an encounter jump dropdown/list that includes monster spawn points and boss groups with type and coordinate labels.
- [x] 2.6 Selecting an entry from the jump list selects the encounter and pans the editor camera to its position.

## 3. Runtime Initialization

- [x] 3.1 Apply `floor(count * random(min, max))` when initializing authored monster spawn point enemies.
- [x] 3.2 Preserve existing monster count behavior for maps without multiplier fields by using `[1, 1]`.
- [x] 3.3 Keep boss group initialization based on explicit boss selections and boss count.
- [x] 3.4 Add runtime source metadata needed to evaluate aggro ranges for monster points and the chosen boss group.

## 4. Runtime Aggro And Chase

- [x] 4.1 Track triggered encounter source IDs for the current battle.
- [x] 4.2 Trigger a monster point source when the player enters its authored aggro range.
- [x] 4.3 Trigger the chosen boss group source when the player enters its authored aggro range.
- [x] 4.4 Mark every living enemy from a triggered source as aggro-locked.
- [x] 4.5 Keep aggro-locked enemies pursuing the player until death or battle reset, including after the player leaves the original aggro range.
- [x] 4.6 Keep untriggered distant enemies lightweight and non-chasing.

## 5. Runtime Visibility And Performance

- [x] 5.1 Allow camera-visible authored enemies to render before aggro so they do not appear to spawn near the player.
- [x] 5.2 Keep offscreen authored enemies out of individual DOM rendering.
- [x] 5.3 Preserve visible enemy DOM budgets and spatial-index based nearby queries.
- [x] 5.4 Ensure enemy HP, death, drops, targeting, damage, and aggro lock state remain correct across runtime state transitions.

## 6. Verification

- [x] 6.1 Extend WebApp smoke coverage for aggro range controls, aggro ring rendering, and aggro drag adjustment.
- [x] 6.2 Extend WebApp smoke coverage for random count multiplier persistence and reload normalization.
- [x] 6.3 Extend WebApp smoke coverage for encounter jump selection and camera pan behavior.
- [x] 6.4 Add runtime checks for group-wide aggro trigger and persistent chase after leaving aggro range.
- [x] 6.5 Add runtime checks that authored enemies are initialized at battle start while offscreen render count remains capped.
- [x] 6.6 Run `npm run build`.
- [x] 6.7 Run `npm test`.
- [x] 6.8 Run `openspec validate extend-map-editor-encounter-aggro --strict`.
