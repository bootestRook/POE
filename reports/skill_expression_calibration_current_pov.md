# Current POV Skill Expression Calibration

## Safety
- Non-destructive: True
- Uses dummy balance: False
- Damage tuning enabled: False

## Current POV
- world_width: 512
- world_height: 512
- camera_zoom: 0.22
- player_speed: 250.0
- enemy_chase_speed: 58.0
- normal_spawn_distance_min: 238.4
- normal_spawn_distance_median: 302.3
- normal_spawn_distance_max: 337.7

## Active Skills
### active_fire_bolt
- `cast.search_range`: 520 -> 380 (avoid whole-map auto targeting while reaching normal spawn pressure)
- `cast.cooldown_ms`: 700 -> 850 (keep baseline auto-cast rhythm visible under current spawn cadence)
- `behavior.params.max_distance`: 520 -> 400 (match projectile reach to current POV engagement distance)
- `behavior.params.projectile_speed`: 520 -> 620 (keep projectile travel visible but not late)
### active_frost_nova
- `cast.search_range`: 430 -> 340 (avoid whole-map auto targeting while reaching normal spawn pressure)
- `cast.cooldown_ms`: 1200 -> 1100 (keep baseline auto-cast rhythm visible under current spawn cadence)
- `behavior.params.radius`: 430 -> 340 (fit area coverage to current spawn cluster)
### active_fungal_petards
- `cast.search_range`: 520 -> 420 (avoid whole-map auto targeting while reaching normal spawn pressure)
- `behavior.params.max_distance`: 520 -> 420 (match projectile reach to current POV engagement distance)
- `behavior.params.projectile_speed`: 690 -> 620 (keep projectile travel visible but not late)
- `modules.*.params.max_distance`: 520 -> 420 (match module projectile reach to current POV)
- `modules.*.params.projectile_speed`: 690 -> 620 (keep module projectile readable)
- `modules.*.params.travel_time_ms`: 760 -> 620 (make delayed projectile land before moving packs drift too far)
- `modules.*.params.radius`: 180 -> 150 (fit triggered area to current spawn cluster)
- `modules.*.trigger.trigger_delay_ms`: 420 -> 320 (keep warning readable without feeling disconnected)
### active_ice_shards
- `cast.search_range`: 560 -> 380 (avoid whole-map auto targeting while reaching normal spawn pressure)
- `cast.cooldown_ms`: 900 -> 820 (keep baseline auto-cast rhythm visible under current spawn cadence)
- `behavior.params.max_distance`: 560 -> 400 (match projectile reach to current POV engagement distance)
- `behavior.params.projectile_speed`: 250 -> 460 (keep projectile travel visible but not late)
- `behavior.params.spread_angle_deg`: 180 -> 70 (keep spread readable in the compact battle view)
### active_lava_orb
- `cast.search_range`: 360 -> 300 (avoid whole-map auto targeting while reaching normal spawn pressure)
- `behavior.params.duration_ms`: 3600 -> 3200 (keep persistent orbit readable without filling the screen forever)
- `behavior.params.tick_interval_ms`: 300 -> 380 (reduce tick spam while preserving rhythm)
- `behavior.params.orbit_radius`: 180 -> 150 (keep orbit near the player under current camera scale)
- `modules.*.params.duration_ms`: 3600 -> 3200 (keep persistent orbit readable)
- `modules.*.params.tick_interval_ms`: 300 -> 380 (control orbit tick visual density)
- `modules.*.params.orbit_radius`: 180 -> 150 (keep orbit close enough to the player)
### active_lightning_chain
- `cast.search_range`: 520 -> 380 (avoid whole-map auto targeting while reaching normal spawn pressure)
- `behavior.params.chain_radius`: 180 -> 165 (fit jump distance to the current encounter cluster)
- `behavior.params.chain_delay_ms`: 120 -> 90 (make chain cadence visible without feeling sluggish)
### active_penetrating_shot
- `cast.search_range`: 680 -> 520 (avoid whole-map auto targeting while reaching normal spawn pressure)
- `behavior.params.max_distance`: 680 -> 520 (match projectile reach to current POV engagement distance)
### active_puncture
- `cast.search_range`: 380 -> 320 (avoid whole-map auto targeting while reaching normal spawn pressure)
- `cast.cooldown_ms`: 760 -> 700 (keep baseline auto-cast rhythm visible under current spawn cadence)
- `behavior.params.length`: 150 -> 260 (make the line skill reach visible enemies in the current POV)
- `behavior.params.width`: 30 -> 72 (make the line skill forgiving enough for moving targets)

## Support Expression Pressure
- `support_fast_attack` `attack_speed_add_percent` 15.0: expression pressure
- `support_fast_cast` `cast_speed_add_percent` 15.0: expression pressure
- `support_skill_haste` `skill_speed_final_percent` 8.0: moderate cadence pressure
- `support_cooldown_focus` `cooldown_reduction_percent` 12.0: moderate cadence pressure
- `support_heavy_impact` `added_cooldown_ms` 120.0: slower cadence tradeoff
- `support_wide_effect` `area_add_percent` 20.0: moderate coverage pressure
- `support_wide_effect` `added_cooldown_ms` 80.0: slower cadence tradeoff
- `support_precision` `projectile_speed_add_percent` -8.0: minor projectile readability pressure
- `support_extra_projectile` `projectile_count_add` 1.0: moderate visual density
- `support_shotgun` `projectile_count_add` 2.0: high visual density
- `support_shotgun` `projectile_speed_add_percent` -20.0: projectile readability pressure
- `support_projectile_speed` `projectile_speed_add_percent` 25.0: projectile readability pressure
- `support_area_magnify` `area_add_percent` 25.0: high coverage pressure
- `support_area_magnify` `skill_speed_final_percent` -10.0: moderate cadence pressure
- `support_overcharge` `added_cooldown_ms` 160.0: slower cadence tradeoff
- `support_overkill` `skill_speed_final_percent` -20.0: high cadence pressure
- `support_projectile_level` `projectile_speed_add_percent` 18.0: minor projectile readability pressure

## Passive Expression Pressure
- `passive_swift_gathering` `move_speed` 10.0: movement changes encounter spacing; review with camera and spawn pressure
