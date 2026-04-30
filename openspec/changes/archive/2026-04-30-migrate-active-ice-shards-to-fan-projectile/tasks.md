## 0. Phase 0: 鐜扮姸鎵弿涓?active_fire_bolt 妯℃澘鑳藉姏纭

- [x] 0.1 鐩爣锛氱‘璁?`refactor-skill-system-runtime-and-skill-package` 宸插綊妗ｏ紝褰撳墠 active changes 涓嶄細闃诲鏈縼绉伙紱鍏佽淇敼鑼冨洿锛氬彧璇?OpenSpec 鐘舵€佷笌鐜版湁鎶€鑳介厤缃紱绂佹瓒婄晫浜嬮」锛氫笉寰椾慨鏀?runtime銆乄ebApp銆乣active_fire_bolt`銆佸簱瀛樸€佹帀钀芥垨瀹濈煶鐩橈紱楠屾敹鏍囧噯锛氳褰?archive 鐘舵€併€乤ctive changes銆乣configs/skills/active/` 褰撳墠鍐呭銆乣active_ice_shards` 鏃?TOML 鐘舵€侊紱鎺ㄨ崘楠岃瘉鍛戒护锛歚cmd /c openspec list --json`
- [x] 0.2 鐩爣锛氱‘璁?`active_fire_bolt` Skill Package銆丼killEditor銆丼kill Test Arena銆丼killEvent 鏃堕棿绾垮拰 AI 鑷祴鎶ュ憡浠嶅彲浣滀负杩佺Щ妯℃澘锛涘厑璁镐慨鏀硅寖鍥达細鍙 `configs/skills/active/active_fire_bolt/skill.yaml`銆乣configs/skills/behavior_templates/projectile.yaml`銆佺浉鍏虫祴璇曞拰 WebApp 琛ㄧ幇鍏ュ彛锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱閲嶆瀯鎴栦慨澶?`active_fire_bolt`锛涢獙鏀舵爣鍑嗭細鍒楀嚭鍙鐢ㄥ瓧娈点€佷簨浠躲€佹祴璇曞満鍜屾姤鍛婅兘鍔涳紱鎺ㄨ崘楠岃瘉鍛戒护锛歚cmd /c openspec validate refactor-skill-system-runtime-and-skill-package --strict` if archived validation is needed, plus existing project tests used by that archived change

## 1. Phase 1: fan_projectile schema / behavior template 璁捐

- [x] 1.1 鐩爣锛氳璁?`configs/skills/behavior_templates/fan_projectile.yaml` 鐨勫瓧娈电櫧鍚嶅崟鍜岀害鏉燂紱鍏佽淇敼鑼冨洿锛歜ehavior template 閰嶇疆銆乻chema 鏍￠獙鐩稿叧鏂囨。鎴栭厤缃紱绂佹瓒婄晫浜嬮」锛氫笉寰楀姞鍏ヨ剼鏈€佽〃杈惧紡 DSL銆佸鏉傝〃杈惧紡瑙ｉ噴鍣ㄦ垨鏈０鏄庡弬鏁伴€忎紶锛涢獙鏀舵爣鍑嗭細瀛楁鍖呭惈 `projectile_count`銆乣projectile_speed`銆乣projectile_width`銆乣projectile_height`銆乣spread_angle`銆乣angle_step`銆乣max_distance`銆乣hit_policy`銆乣collision_radius`銆乣spawn_pattern`銆乣per_projectile_damage_scale`锛屽苟鏈夌被鍨嬨€佽寖鍥淬€佹灇涓剧害鏉燂紱鎺ㄨ崘楠岃瘉鍛戒护锛歚cmd /c openspec validate migrate-active-ice-shards-to-fan-projectile --strict`
- [x] 1.2 鐩爣锛氭槑纭?`fan_projectile` 涓庢棦鏈?`projectile` 妯℃澘鐨勫鐢ㄨ竟鐣岋紱鍏佽淇敼鑼冨洿锛歋killRuntime template registry / validation design锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱鎶?`fan_projectile` 鍚堝苟鎴愬墠绔瑙夌壒鍒わ紱楠屾敹鏍囧噯锛氳璁¤鏄庡啓娓呭鎶曞皠鎵囧舰鏂瑰悜銆佺嫭绔?spawn銆佺湡瀹?hit/damage 鐨勪簨浠跺绾︼紱鎺ㄨ崘楠岃瘉鍛戒护锛歱roject schema validation command used by existing skill package tests

## 2. Phase 2: active_ice_shards Skill Package 鍒涘缓

- [x] 2.1 鐩爣锛氬垱寤烘湭鏉?`configs/skills/active/active_ice_shards/skill.yaml`锛涘厑璁镐慨鏀硅寖鍥达細浠?`active_ice_shards` Skill Package 鍜屽繀瑕?localization keys锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱杩佺Щ鍏朵粬 6 涓富鍔ㄦ妧鑳斤紝涓嶅緱淇敼姝ｅ紡鎺夎惤銆佸簱瀛樸€佸疂鐭崇洏锛屼笉寰楀紩鍏ヨ嫳鏂囩帺瀹跺彲瑙佹枃妗堬紱楠屾敹鏍囧噯锛歱ackage 鍖呭惈 id銆乿ersion銆乨isplay銆乧lassification銆乧ast銆乥ehavior銆乭it銆乻caling銆乸resentation銆乸review锛屽苟澹版槑 `classification.damage_type = cold`銆乣behavior.template = fan_projectile`锛涙帹鑽愰獙璇佸懡浠わ細skill package validation command used by current `active_fire_bolt`
- [x] 2.2 鐩爣锛氫繚鐣欐棫璺緞鍏煎鐩村埌杩佺Щ瀹屾暣楠屾敹閫氳繃锛涘厑璁镐慨鏀硅寖鍥达細鍔犺浇椤哄簭鎴栬縼绉诲紑鍏崇浉鍏虫渶灏忛€昏緫锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱鍗婅縼绉诲鑷?`active_ice_shards` 鍦ㄧ紪杈戝櫒鍙墦寮€浣嗚繍琛屾椂涓嶅彲鐢紱楠屾敹鏍囧噯锛氳縼绉诲畬鎴愬墠鏃ц涓轰粛鍙敤锛岃縼绉诲畬鎴愬悗浠?Skill Package 鍔犺浇锛涙帹鑽愰獙璇佸懡浠わ細existing backend skill loading tests

## 3. Phase 3: SkillEditor 鏂板 fan_projectile 妯″潡瀛楁

- [x] 3.1 鐩爣锛氭柊澧?SkillEditor `fan_projectile` 瀛愬脊妯″潡锛涘厑璁镐慨鏀硅寖鍥达細SkillEditor 琛ㄥ崟銆佸瓧娈垫槧灏勩€佷繚瀛樻牎楠屻€佸彧璇婚琛屾椂闂存憳瑕侊紱绂佹瓒婄晫浜嬮」锛氫笉寰楀啓鍏ユā鏉挎湭澹版槑瀛楁锛屼笉寰楃敤闅愯棌瀛楁淇濆瓨娲剧敓椋炶鏃堕棿锛屼笉寰楀垱寤鸿妭鐐圭紪杈戝櫒锛涢獙鏀舵爣鍑嗭細缂栬緫鍣ㄦ毚闇?`projectile_count`銆乣projectile_speed`銆乣projectile_width`銆乣projectile_height`銆乣spread_angle`銆乣angle_step`銆乣max_distance`銆乣hit_policy`銆乣collision_radius`銆乣spawn_pattern`銆乣per_projectile_damage_scale` 鍜屽彧璇婚琛屾椂闂存憳瑕侊紱鎺ㄨ崘楠岃瘉鍛戒护锛歐ebApp build/test command used by current SkillEditor
- [x] 3.2 鐩爣锛氳ˉ榻愬瓧娈垫牎楠岋紱鍏佽淇敼鑼冨洿锛歴chema/template whitelist validation and Chinese error display锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱鍓嶇缁曡繃 schema 淇濆瓨闈炴硶鍙傛暟锛涢獙鏀舵爣鍑嗭細姝ｆ暣鏁般€佹鏁般€佽搴﹁寖鍥淬€佹灇涓俱€乨amage scale 鑼冨洿鍜屾湭鐭ュ瓧娈垫嫆缁濆潎鍙獙璇侊紱鎺ㄨ崘楠岃瘉鍛戒护锛歋killEditor save validation tests and `cmd /c openspec validate migrate-active-ice-shards-to-fan-projectile --strict`

## 4. Phase 4: SkillRuntime 瀹炵幇 fan_projectile

- [x] 4.1 鐩爣锛氬疄鐜颁粠鐜╁浣嶇疆鎴栭噴鏀炬簮浣嶇疆鐢熸垚澶氭灇鎵囧舰鎶曞皠鐗╋紱鍏佽淇敼鑼冨洿锛歋killRuntime behavior template registry銆乫an projectile event generation銆乧ollision/hit helper tests锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱閲婃斁鐬棿鎵ｈ锛屼笉寰楃敤闈欐€佸亣浜嬩欢锛屼笉寰楀湪 Combat Runtime 鍐欏叿浣撴妧鑳藉垎鏀紱楠屾敹鏍囧噯锛氭瘡鏋氭姇灏勭墿鏈夌嫭绔嬫柟鍚戝拰 `projectile_spawn`锛屾柟鍚戝洿缁曟渶杩戞晫浜烘垨閰嶇疆鐩爣鏂瑰悜灞曞紑锛涙帹鑽愰獙璇佸懡浠わ細backend SkillRuntime tests for fan projectile event count and directions
- [x] 4.2 鐩爣锛氬疄鐜扮湡瀹炲懡涓€佷激瀹冲拰琛ㄧ幇浜嬩欢鏃跺簭锛涘厑璁镐慨鏀硅寖鍥达細SkillRuntime damage timing and SkillEvent payload generation锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱璺宠繃 `projectile_hit`锛屼笉寰楄 VFX 浠ｆ浛浼ゅ缁撶畻锛屽墠绔笉寰楃寽浼ゅ鏃舵満锛涢獙鏀舵爣鍑嗭細鍛戒腑鍚庤緭鍑?`projectile_hit`銆乣damage`銆乣hit_vfx`銆乣floating_text`锛宍damage_type = cold`锛宒amage 涓嶆棭浜?spawn/travel/hit锛涙帹鑽愰獙璇佸懡浠わ細backend SkillEvent timeline tests

## 5. Phase 5: WebApp 娑堣垂 fan_projectile SkillEvent

- [x] 5.1 鐩爣锛氳 WebApp 浣跨敤鐪熷疄 `fan_projectile` SkillEvents 娓叉煋澶氭灇鍐版１锛涘厑璁镐慨鏀硅寖鍥达細SkillEvent consumption, projectile presentation, hit VFX, floating text rendering锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱閫氳繃 `behavior_type`銆乣visual_effect` 鎴?skill id 鐚滄妧鑳借涓猴紝涓嶅緱鏂板闈欐€佸亣浜嬩欢锛涢獙鏀舵爣鍑嗭細WebApp 鏍规嵁浜嬩欢涓殑 position銆乨irection銆乨uration銆乼arget銆乤mount銆乨amage_type銆乿fx_key銆乺eason_key 娓叉煋鎶曞皠銆佸懡涓拰娴瓧锛涙帹鑽愰獙璇佸懡浠わ細WebApp build/test command plus browser arena smoke test
- [x] 5.2 鐩爣锛氫繚鎸佷腑鏂囩帺瀹跺彲瑙佸弽棣堬紱鍏佽淇敼鑼冨洿锛歭ocalization and display mapping锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱寮曞叆鑻辨枃鐜╁鍙鏂囨锛涢獙鏀舵爣鍑嗭細HUD銆佹诞瀛椼€侀敊璇拰鎶ュ憡灞曠ず鍧囦负涓枃锛涙帹鑽愰獙璇佸懡浠わ細localization validation used by project tests

## 6. Phase 6: Skill Test Arena 鎺ュ叆鍐版１鏁ｅ皠

- [x] 6.1 鐩爣锛氬湪 Skill Test Arena 鏀寔閫夋嫨骞惰繍琛?`active_ice_shards`锛涘厑璁镐慨鏀硅寖鍥达細arena skill selection, scenario runner, result model锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱鍐欑湡瀹?inventory銆乬em instance銆乸roduction skill files锛涢獙鏀舵爣鍑嗭細鍗曚綋鏈ㄦ々銆佷笁鐩爣妯帓銆佸瘑闆嗗皬鎬潎鍙繍琛屽啺妫辨暎灏勶紱鎺ㄨ崘楠岃瘉鍛戒护锛歛rena test/report generation command used by current `active_fire_bolt`
- [x] 6.2 鐩爣锛氶獙璇佸弬鏁板彉鍖栧奖鍝嶇湡瀹炴晥鏋滐紱鍏佽淇敼鑼冨洿锛歛rena modifier stack and runtime param override tests锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱鍙敼 UI 鏁板瓧涓嶅奖鍝?SkillEvents锛涢獙鏀舵爣鍑嗭細淇敼 `projectile_count` 鏀瑰彉 spawn 鏁伴噺锛屼慨鏀?`spread_angle` 鏀瑰彉鏂瑰悜鍒嗗竷锛屼慨鏀?`projectile_speed` 鏀瑰彉椋炶鏃堕棿锛孧odifier 娴嬭瘯鏍堝奖鍝嶆渶缁堜激瀹虫垨鎶曞皠鐗╁弬鏁帮紱鎺ㄨ崘楠岃瘉鍛戒护锛歵argeted arena scenario tests

## 7. Phase 7: SkillEvent 鏃堕棿绾夸笌 AI 鑷祴鎶ュ憡鎺ュ叆鍐版１鏁ｅ皠

- [x] 7.1 鐩爣锛歋killEvent 鏃堕棿绾垮睍绀哄啺妫辨暎灏勭湡瀹炰簨浠讹紱鍏佽淇敼鑼冨洿锛歵imeline event display and field mapping锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱灞曠ず闈欐€佺ず渚嬩簨浠讹紝涓嶅緱闅愯棌鍏抽敭瀛楁锛涢獙鏀舵爣鍑嗭細鏄剧ず `cast_start`銆佸鏉?`projectile_spawn`銆乣projectile_hit`銆乣damage`銆乣hit_vfx`銆乣floating_text`銆佸瓨鍦ㄦ椂鐨?`cooldown_update`锛屽瓧娈靛寘鍚?`timestamp_ms`銆乣delay_ms`銆乣duration_ms`銆乣source_entity`銆乣target_entity`銆乣amount`銆乣damage_type`銆乣vfx_key`銆乣reason_key`銆乣payload`锛涙帹鑽愰獙璇佸懡浠わ細timeline component/test command used by current Skill Test Arena
- [x] 7.2 鐩爣锛欰I 鑷祴鎶ュ憡鎸夌湡瀹炴祴璇曠粨鏋滆瘎浼板啺妫辨暎灏勶紱鍏佽淇敼鑼冨洿锛歳eport input mapping, checks, Chinese output锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱鍩轰簬闈欐€佸亣浜嬩欢鎴栨墜鍐欑粨璁虹敓鎴愰€氳繃锛涢獙鏀舵爣鍑嗭細鎶ュ憡妫€鏌ュ鏋?spawn銆佹墖褰㈡柟鍚戙€乭it銆乨amage銆乭it_vfx銆乫loating_text銆乨amage 鏃跺簭銆侀琛屾湡闂存湭鎵ｈ銆乧old 绫诲瀷銆乸rojectile_count 鍜?spread_angle 鏀瑰姩鏁堟灉锛屽苟杈撳嚭 `閫氳繃` / `閮ㄥ垎閫氳繃` / `涓嶉€氳繃`銆佷腑鏂囦笉涓€鑷撮」鍜屽缓璁慨澶嶉」锛涙帹鑽愰獙璇佸懡浠わ細`python tools/generate_skill_test_report.py` with active ice shards scenario once implemented

## 8. Phase 8: 楠岃瘉涓庡洖褰?
- [x] 8.1 鐩爣锛氳繍琛?OpenSpec 鍜岄厤缃弗鏍奸獙璇侊紱鍏佽淇敼鑼冨洿锛歰nly fixes required by spec/config validation inside this change scope锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱鍊熼獙璇佸け璐ラ噸鏋勬棤鍏虫ā鍧楋紱楠屾敹鏍囧噯锛歄penSpec strict validate passes and skill package/template validation passes锛涙帹鑽愰獙璇佸懡浠わ細`cmd /c openspec validate migrate-active-ice-shards-to-fan-projectile --strict`
- [x] 8.2 鐩爣锛氳繍琛?SkillRuntime銆丼killEditor銆丼kill Test Arena銆丼killEvent timeline銆丄I report targeted regression锛涘厑璁镐慨鏀硅寖鍥达細only scoped fixes for ice shards migration and shared behavior template plumbing锛涚姝㈣秺鐣屼簨椤癸細涓嶅緱鐮村潖 `active_fire_bolt`锛屼笉寰楄縼绉诲叾浠栨妧鑳斤紱楠屾敹鏍囧噯锛歚active_fire_bolt` existing tests remain green, `active_ice_shards` fan projectile acceptance passes in required scenarios, report conclusion matches actual results锛涙帹鑽愰獙璇佸懡浠わ細project backend tests, WebApp build/test, targeted arena/report tests

