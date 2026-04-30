---
name: projectile-vfx-standard-production
description: Create or retrofit projectile skill VFX for this POE project. Use when asked to make or modify effects for skills tagged or described as projectile, pierce, chain, ranged, spell projectile, fan/spread shots, or any runtime projectile-driven skill. Enforce runtime projectile data as the single source of truth and prevent VFX from recalculating trajectory, direction, hit position, targeting, damage, cooldown, or combat logic.
---

# Projectile VFX Standard Production

## Goal

Produce or retrofit VFX for projectile skills while keeping the runtime projectile as the only source of truth. VFX must render the projectile's real spawn point, direction, center, trajectory, and hit point; it must never calculate a separate visual ballistic path.

## Before Editing

1. Follow the repository `AGENTS.md` process before changing files.
2. Identify the requested skill, branch, scoped files, forbidden files, smallest implementation path, and verification method.
3. Stop and ask if the target skill or projectile runtime API is ambiguous.
4. Do not change combat values, cooldowns, damage, hit rules, targeting, projectile logic, or unrelated skills.

For non-trivial work, state a short plan in this format:

```text
Plan:
1. Inspect [area/file] -> verify: understand current behavior
2. Change [specific file/module] -> verify: minimal diff only
3. Run [test/build/check] -> verify: pass/fail result
```

## Runtime Binding Rules

Treat these runtime projectile fields as authoritative whenever available:

- `projectileId`
- `skillId`
- `spawnWorldPosition`
- `directionWorld`
- `velocityWorld`
- `currentWorldPosition`
- `hitWorldPosition`
- `projectileIndex`
- `projectileCount`
- `localSpreadAngle`
- `fanAngle`
- `pierceRemaining`
- `chainRemaining`
- `lifetimeMs`

Apply these bindings:

- VFX muzzle/cast position = `spawnWorldPosition`
- VFX flight direction = normalized `velocityWorld`; fall back to `directionWorld` only if velocity is unavailable
- VFX body center = `currentWorldPosition`
- VFX impact position = `hitWorldPosition`
- VFX projectile identity = `projectileId`
- Multi-projectile skills must create one independent VFX instance per runtime projectile

Never derive projectile VFX direction from mouse position, target center, enemy position, screen delta, or a separate visual trajectory.

## Standard VFX Layers

Build projectile effects as four layers when the engine supports them:

1. Cast / Muzzle
   - Trigger at projectile spawn.
   - Attach to `spawnWorldPosition`.

2. Projectile Body
   - Render the projectile's visible body.
   - Follow `currentWorldPosition` every frame.

3. Trail
   - Render trail, afterimage, particles, or beam-like motion.
   - Align to the normalized runtime velocity and speed.

4. Impact
   - Trigger only when the runtime projectile ends or hits.
   - Spawn at `hitWorldPosition`.

If the existing engine uses different names, map the local concepts to these four layers without refactoring unrelated systems.

## Coordinates and Direction

- Use world coordinates for runtime projectile state.
- Use the project's existing world-to-screen projection for rendering.
- Do not infer logic direction from screen-space deltas.
- In 2.5D or isometric projection, keep runtime values in world space and render from projected coordinates.
- Compute visual rotation from world direction using the project's established world-to-render angle conversion.

## Art Facing Offset

Before changing rotation code, identify the asset's default facing:

- right-facing
- up-facing
- another documented direction

Use a named constant such as `PROJECTILE_ART_FACING_OFFSET_DEG` to correct visual asset orientation. Do not mix art-facing correction into projectile logic, velocity, targeting, or hit detection.

## Debug Requirements

When debug rendering is available, add or preserve Chinese labels for:

- 逻辑发射点
- 特效发射点
- 逻辑飞行方向
- 特效朝向
- projectile center
- 命中点

The debug layer should make it possible to compare runtime projectile data against VFX placement and orientation.

## Acceptance Criteria

Verify the result against these requirements:

- VFX start point differs from projectile spawn by no more than 2 px.
- VFX direction differs from projectile direction by no more than 3 degrees.
- Projectile body does not drift from `currentWorldPosition` during flight.
- Impact VFX appears at the true `hitWorldPosition`.
- Eight-direction projectile tests pass.
- Near target, far target, and moving target tests pass when the project has those scenarios.
- No skill damage, cooldown, hit, targeting, or combat numeric behavior changed.

## Forbidden Changes

- Do not let VFX recalculate direction from mouse, target center, or enemy position.
- Do not let trails use a different start point from the runtime projectile.
- Do not fix visual orientation by changing projectile logic.
- Do not modify unrelated skills.
- Do not expand work into combat value or balance layers.
