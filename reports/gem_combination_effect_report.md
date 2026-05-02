# Gem Combination Effect Report

## Safety
- Non-destructive: True
- Wrote production state: False

## Summary
- Cases: 4
- Passed checks: 10/10
- Observations: 0

## Cases
### fire_bolt_supports_and_passive
- Board valid: True
- Checks passed: 3/3
- Baseline: {"applied_modifiers": [], "area_multiplier": 1.0, "base_gem_id": "active_fire_bolt", "final_cooldown_ms": 700, "final_damage": 12.0, "projectile_count": 1, "projectile_speed": 520.0, "radius": null, "speed_multiplier": 1.0}
- Combo: {"applied_modifiers": [{"layer": "additive", "reason": "modifier.support_base", "relation": "adjacent", "source": "support_extra_projectile", "stat": "projectile_count_add", "target": "active_fire_bolt", "value": 1.25}, {"layer": "final", "reason": "modifier.support_base", "relation": "adjacent", "source": "support_extra_projectile", "stat": "damage_final_percent", "target": "active_fire_bolt", "value": -12.5}, {"layer": "additive", "reason": "modifier.support_base", "relation": "adjacent", "source": "support_fire_mastery", "stat": "fire_damage_add_percent", "target": "active_fire_bolt", "value": 22.5}, {"layer": "additive", "reason": "modifier.support_to_passive", "relation": "adjacent", "source": "support_fire_mastery", "stat": "fire_damage_add_percent", "target": "passive_fire_focus", "value": 22.5}, {"layer": "additive", "reason": "modifier.passive_base", "relation": "same_box", "source": "passive_fire_focus", "stat": "fire_damage_add_percent", "target": "active_fire_bolt", "value": 32.5}], "area_multiplier": 1.0, "base_gem_id": "active_fire_bolt", "final_cooldown_ms": 700, "final_damage": 18.637499999999996, "projectile_count": 2, "projectile_speed": 520.0, "radius": null, "speed_multiplier": 1.0}
- projectile_count_changed: PASS
- damage_changed_by_fire_supports: PASS
- projectile_spawn_matches_count: PASS

### frost_nova_area_and_cooldown_interaction
- Board valid: True
- Checks passed: 3/3
- Baseline: {"applied_modifiers": [], "area_multiplier": 1.0, "base_gem_id": "active_frost_nova", "final_cooldown_ms": 1200, "final_damage": 14.0, "projectile_count": 1, "projectile_speed": null, "radius": 430.0, "speed_multiplier": 1.0}
- Combo: {"applied_modifiers": [{"layer": "additive", "reason": "modifier.support_base", "relation": "adjacent", "source": "support_area_magnify", "stat": "area_add_percent", "target": "active_frost_nova", "value": 31.25}, {"layer": "final", "reason": "modifier.support_base", "relation": "adjacent", "source": "support_area_magnify", "stat": "skill_speed_final_percent", "target": "active_frost_nova", "value": -12.5}, {"layer": "additive", "reason": "modifier.support_base", "relation": "same_column", "source": "support_cooldown_focus", "stat": "cooldown_reduction_percent", "target": "active_frost_nova", "value": 20.0}, {"layer": "final", "reason": "modifier.support_base", "relation": "same_column", "source": "support_cooldown_focus", "stat": "damage_final_percent", "target": "active_frost_nova", "value": -5.0}], "area_multiplier": 1.3125, "base_gem_id": "active_frost_nova", "final_cooldown_ms": 1097, "final_damage": 13.299999999999999, "projectile_count": 1, "projectile_speed": null, "radius": 564.375, "speed_multiplier": 0.875}
- area_radius_increased: PASS
- area_support_applied: PASS
- cooldown_focus_applied: PASS

### same_row_conduit_amplification
- Board valid: True
- Checks passed: 2/2
- Baseline same-row support: {"applied_modifiers": [{"layer": "additive", "reason": "modifier.support_base", "relation": "same_row", "source": "support_fire_mastery", "stat": "fire_damage_add_percent", "target": "active_fire_bolt", "value": 18.0}], "area_multiplier": 1.0, "base_gem_id": "active_fire_bolt", "final_cooldown_ms": 700, "final_damage": 14.16, "projectile_count": 1, "projectile_speed": 520.0, "radius": null, "speed_multiplier": 1.0}
- Combo with conduit: {"applied_modifiers": [{"layer": "final", "reason": "modifier.conduit_amplifier", "relation": "same_row", "source": "support_row_conduit", "stat": "conduit_multiplier", "target": "active_fire_bolt", "value": 1.25}, {"layer": "additive", "reason": "modifier.support_base", "relation": "same_row", "source": "support_fire_mastery", "stat": "fire_damage_add_percent", "target": "active_fire_bolt", "value": 22.5}], "area_multiplier": 1.0, "base_gem_id": "active_fire_bolt", "final_cooldown_ms": 700, "final_damage": 14.700000000000001, "projectile_count": 1, "projectile_speed": 520.0, "radius": null, "speed_multiplier": 1.0}
- conduit_multiplier_present: PASS
- conduit_increases_support_value: PASS

### self_stat_passives
- Board valid: True
- Checks passed: 2/2
- Player stats: {"max_life": {"label_text": "最大生命", "value": 125.0}, "move_speed": {"label_text": "移动速度", "value": 1.1}}
- max_life_increased: PASS
- move_speed_increased: PASS
