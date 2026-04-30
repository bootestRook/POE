## 1. Phase 0: 鐜扮姸鎵弿涓庡凡杩佺Щ鎶€鑳芥ā鏉胯兘鍔涚‘璁?
鐩爣锛氱‘璁ゅ墠缃湴鍒?/ `damage_zone` change 宸插綊妗ｏ紝纭褰撳墠 active changes銆佸凡杩佺Щ Skill Package銆乣active_lightning_chain` 鏃ц矾寰勫拰鐜版湁 SkillEditor / Skill Test Arena / SkillEvent 鏃堕棿绾?/ AI 鑷祴鎶ュ憡鑳藉姏銆?
鍏佽淇敼鑼冨洿锛氭棤浠ｇ爜淇敼锛涘彧鍏佽璇诲彇 OpenSpec銆侀厤缃€佹簮鐮佸拰娴嬭瘯鐘舵€併€?
绂佹瓒婄晫浜嬮」锛氫笉寰椾慨鏀?complete 浣嗘湭褰掓。鐨勫叾浠?change artifacts锛涗笉寰楀垱寤?`active_lightning_chain/skill.yaml`锛涗笉寰楄縼绉诲叾浠栨妧鑳姐€?
楠屾敹鏍囧噯锛氱‘璁や笂涓€涓湴鍒?/ `damage_zone` 鐩稿叧 change 宸插綊妗ｏ紱纭宸茶縼绉?Skill Package 鑷冲皯鍖呭惈 `active_fire_bolt`銆乣active_ice_shards`銆乣active_penetrating_shot`銆乣active_frost_nova`銆乣active_puncture`锛涚‘璁?`active_lightning_chain` 浠嶈蛋鏃?`skill_templates.toml`锛屼笖 `configs/skills/active/active_lightning_chain/skill.yaml` 褰撳墠涓嶅瓨鍦ㄣ€?
鎺ㄨ崘楠岃瘉鍛戒护锛歚cmd /c openspec list --json`銆乣Test-Path openspec\changes\archive\2026-04-30-unify-frost-nova-and-ground-spike-as-damage-zone`銆乣Get-ChildItem configs\skills\active`銆乣Select-String -Path configs\skills\skill_templates.toml -Pattern "lightning_chain"`銆乣Test-Path configs\skills\active\active_lightning_chain\skill.yaml`銆?
- [x] 1.1 纭涓婁竴涓湴鍒?/ `damage_zone` 鐩稿叧 change 宸插畬鎴愬苟褰掓。銆?- [x] 1.2 璁板綍褰撳墠 active changes 鐘舵€侊紝骞剁‘璁や笉淇敼鍏朵粬 active change artifacts銆?- [x] 1.3 纭宸茶縼绉?Skill Package 鍖呭惈 `active_fire_bolt`銆乣active_ice_shards`銆乣active_penetrating_shot`銆乣active_frost_nova`銆乣active_puncture`銆?- [x] 1.4 纭 `active_lightning_chain` 浠嶅湪鏃?`skill_templates.toml` 璺緞锛屼笖鏂?Skill Package 鏂囦欢涓嶅瓨鍦ㄣ€?- [x] 1.5 纭 SkillEditor銆丼kill Test Arena銆丼killEvent 鏃堕棿绾垮拰 AI 鑷祴鎶ュ憡鐜版湁鑳藉姏鍙綔涓鸿縼绉绘ā鏉裤€?
## 2. Phase 1: `chain` schema / behavior template 璁捐

鐩爣锛氭柊澧炲０鏄庡紡 `chain` behavior template 鍜?schema / 閰嶇疆鏍￠獙锛屽缓绔嬪瓧娈电櫧鍚嶅崟鍜岀害鏉熴€?
鍏佽淇敼鑼冨洿锛歚configs/skills/behavior_templates/chain.yaml`銆乣configs/skills/schema/skill.schema.json`銆乣tools/validate_v1_configs.py`銆佺浉鍏抽厤缃牎楠屾祴璇曘€?
绂佹瓒婄晫浜嬮」锛氫笉寰楀垱寤鸿剼鏈?DSL銆佸鏉傝〃杈惧紡瑙ｉ噴鍣ㄣ€佹湭澹版槑鍙傛暟銆佸墠绔笓灞炲亣鍙傛暟锛涗笉寰楀疄鐜拌繍琛屾椂涓撳睘鎶€鑳藉垎鏀紱涓嶅緱杩佺Щ鍏朵粬鎶€鑳姐€?
楠屾敹鏍囧噯锛歚chain` 妯℃澘澹版槑 `chain_count`銆乣chain_radius`銆乣chain_delay_ms`銆乣damage_falloff_per_chain`銆乣target_policy`銆乣allow_repeat_target`銆乣max_targets`銆乣segment_vfx_key`锛涢潪娉曠被鍨嬨€侀潪娉曡寖鍥淬€佹湭鐭ュ瓧娈点€佽剼鏈?DSL 瀛楁鍧囪鎷掔粷銆?
鎺ㄨ崘楠岃瘉鍛戒护锛歚python tools\validate_v1_configs.py`銆乣python -m unittest tests.test_skill_editor tests.test_skill_effects`銆?
- [x] 2.1 鏂板 `configs/skills/behavior_templates/chain.yaml`锛屽０鏄?`chain` 瀛楁鐧藉悕鍗曘€?- [x] 2.2 鎵╁睍 schema / 閰嶇疆鏍￠獙锛屾敮鎸?`chain` 骞舵嫆缁濇湭澹版槑瀛楁銆?- [x] 2.3 鏍￠獙 `chain_count` 涓烘鏁存暟銆?- [x] 2.4 鏍￠獙 `chain_radius` 涓烘鏁般€?- [x] 2.5 鏍￠獙 `chain_delay_ms` 涓洪潪璐熸暟銆?- [x] 2.6 鏍￠獙 `damage_falloff_per_chain` 涓哄悎娉曟暟鍊艰寖鍥淬€?- [x] 2.7 鏍￠獙 `target_policy` 涓烘灇涓撅紝绗竴鐗堣嚦灏戞敮鎸?`nearest_not_hit`銆?- [x] 2.8 鏍￠獙 `allow_repeat_target` 涓哄竷灏斿€间笖榛樿 `false`銆?- [x] 2.9 鏍￠獙 `max_targets` 涓烘鏁存暟鎴栨槑纭０鏄庣殑 `unlimited` 鏋氫妇銆?- [x] 2.10 鏍￠獙 `segment_vfx_key` 鍙兘鍐?key銆?- [x] 2.11 娣诲姞妯℃澘鍜?schema 鏍￠獙娴嬭瘯锛岃鐩栧悎娉曢厤缃€侀潪娉曡寖鍥淬€侀潪娉曟灇涓俱€侀潪娉?key銆佹湭鐭ュ瓧娈靛拰鑴氭湰/DSL 瀛楁銆?
## 3. Phase 2: `active_lightning_chain` Skill Package 鍒涘缓

鐩爣锛氭柊澧?`active_lightning_chain` Skill Package锛屼娇杩為攣闂數浠庢棫妯℃澘杩佺Щ鍒?`chain` behavior template銆?
鍏佽淇敼鑼冨洿锛歚configs/skills/active/active_lightning_chain/skill.yaml`銆乣configs/localization/zh_cn.toml`銆侀厤缃牎楠屾祴璇曘€?
绂佹瓒婄晫浜嬮」锛氫笉寰楄縼绉?`active_lava_orb`銆乣active_fungal_petards` 鎴栧叾浠栦富鍔ㄦ妧鑳斤紱涓嶅緱淇敼宸茶縼绉绘妧鑳借兘鍔涳紱涓嶅緱淇敼姝ｅ紡鎺夎惤銆佸簱瀛樸€佸疂鐭崇洏锛涗笉寰楀紩鍏ヨ嫳鏂囩帺瀹跺彲瑙佹枃妗堛€?
楠屾敹鏍囧噯锛歚active_lightning_chain/skill.yaml` 瀛樺湪骞堕€氳繃 schema 鏍￠獙锛涘０鏄?`behavior.template = chain`锛涘０鏄?`classification.damage_type = lightning`锛涚帺瀹跺彲瑙佹枃鏈娇鐢ㄤ腑鏂囨湰鍦板寲 key锛涙湭杩佺Щ鎶€鑳戒粛鏈縼绉汇€?
鎺ㄨ崘楠岃瘉鍛戒护锛歚python tools\validate_v1_configs.py`銆乣python -m unittest tests.test_skill_effects tests.test_combat`銆?
- [x] 3.1 鏂板 `configs/skills/active/active_lightning_chain/skill.yaml`銆?- [x] 3.2 濉啓 Skill Package 鍩虹缁撴瀯锛歚id`銆乣version`銆乣display`銆乣classification`銆乣cast`銆乣behavior`銆乣hit`銆乣scaling`銆乣presentation`銆乣preview`銆?- [x] 3.3 璁剧疆 `behavior.template = chain` 骞跺～鍐欏悎娉?`behavior.params`銆?- [x] 3.4 璁剧疆 `classification.damage_type = lightning`銆?- [x] 3.5 娣诲姞鎴栧鐢ㄤ腑鏂囨湰鍦板寲 key锛岀‘淇濇墍鏈夌帺瀹跺彲瑙佹枃鏈负涓枃銆?- [x] 3.6 娣诲姞閰嶇疆娴嬭瘯锛岃瘉鏄?`active_lightning_chain` 浣跨敤 `chain`銆乴ightning damage type锛屽苟閫氳繃 schema 鏍￠獙銆?- [x] 3.7 纭 `active_lava_orb` 鍜?`active_fungal_petards` 浠嶆棤 Skill Package銆?
## 4. Phase 3: SkillEditor 鏂板 `chain` 妯″潡瀛楁

鐩爣锛氬湪 SkillEditor 涓柊澧炶繛閿佹ā鍧楋紝鍏佽缂栬緫 `chain` 鍏ㄩ儴瀛楁骞舵樉绀哄彧璇绘憳瑕併€?
鍏佽淇敼鑼冨洿锛歚src/liufang/skill_editor.py`銆乣webapp/App.tsx` 涓?SkillEditor 鐩稿叧 UI銆乣webapp/styles.css` 涓繀瑕佹牱寮忋€乣tests/test_skill_editor.py`銆乣webapp/smoke-test.mjs`銆?
绂佹瓒婄晫浜嬮」锛氫笉寰楁妸杩為攣閫昏緫鍐欐垚鍓嶇涓撳睘鍋囧弬鏁帮紱涓嶅緱缁曡繃 schema 鍜?template 鐧藉悕鍗曪紱涓嶅緱寮曞叆鑻辨枃鐜╁鍙鏂囨锛涗笉寰楁仮澶嶉殢鏈鸿瘝缂€ UI銆?
楠屾敹鏍囧噯锛歋killEditor 鏄剧ず `chain_count`銆乣chain_radius`銆乣chain_delay_ms`銆乣damage_falloff_per_chain`銆乣target_policy`銆乣allow_repeat_target`銆乣max_targets`銆乣segment_vfx_key`銆佸彧璇绘渶澶ч摼娈垫憳瑕併€佸彧璇婚璁￠摼鎬绘椂闀挎憳瑕侊紱闈炴硶瀛楁鍜屽€间腑鏂囨姤閿欎笖涓嶄繚瀛樸€?
鎺ㄨ崘楠岃瘉鍛戒护锛歚python -m unittest tests.test_skill_editor`銆乣cmd /c npm test`銆?
- [x] 4.1 鏂板 SkillEditor `chain` 杩為攣妯″潡銆?- [x] 4.2 鏆撮湶鍏ㄩ儴 `chain` 鍙紪杈戝瓧娈点€?- [x] 4.3 涓?`target_policy` 浣跨敤鏋氫妇鎺т欢銆?- [x] 4.4 涓?`allow_repeat_target` 浣跨敤甯冨皵鎺т欢銆?- [x] 4.5 涓?`chain_count` 鍜?`max_targets` 娣诲姞鏁存暟鏍￠獙銆?- [x] 4.6 涓?`chain_radius`銆乣chain_delay_ms`銆乣damage_falloff_per_chain` 娣诲姞鑼冨洿鏍￠獙銆?- [x] 4.7 涓?`segment_vfx_key` 娣诲姞 key-only 鏍￠獙锛屼笖涓嶄綔涓虹帺瀹跺彲瑙佹枃妗堛€?- [x] 4.8 鏄剧ず鍙鏈€澶ч摼娈垫憳瑕佸拰鍙棰勮閾炬€绘椂闀挎憳瑕併€?- [x] 4.9 淇濆瓨鍓嶆墽琛?schema 涓?behavior template 鐧藉悕鍗曟牎楠屻€?- [x] 4.10 娣诲姞娴嬭瘯瑕嗙洊闈炴硶 `chain_count`銆乣chain_radius`銆乣chain_delay_ms`銆乣damage_falloff_per_chain`銆乣target_policy`銆乣allow_repeat_target`銆乣max_targets`銆乣segment_vfx_key` 鍜屾湭鐭ュ瓧娈点€?
## 5. Phase 4: SkillRuntime 瀹炵幇 `chain`

鐩爣锛氬疄鐜伴€氱敤 `chain` 琛屼负妯℃澘锛岀敓鎴愮湡瀹為摼娈点€佷激瀹冲拰琛ㄧ幇浜嬩欢銆?
鍏佽淇敼鑼冨洿锛歚src/liufang/skill_runtime.py`銆乣src/liufang/skill_effects.py`銆乣tests/test_skill_runtime.py`銆乣tests/test_skill_effects.py`銆乣tests/test_combat.py`銆?
绂佹瓒婄晫浜嬮」锛氫笉寰楀啓 `active_lightning_chain` 涓撳睘 Combat Runtime 鍒嗘敮锛涗笉寰楀彧鐢讳竴鏉＄嚎锛涗笉寰楅噴鏀剧灛闂翠竴娆℃€ф墸琛€锛涗笉寰椾娇鐢ㄩ潤鎬佸亣浜嬩欢锛涗笉寰椾慨鏀瑰凡杩佺Щ鎶€鑳借涓恒€?
楠屾敹鏍囧噯锛歊untime 閫夋嫨鏈€杩戞晫浜轰綔涓哄垵濮嬬洰鏍囷紱鎸?`chain_radius`銆乣target_policy`銆乣allow_repeat_target`銆乣chain_count`銆乣max_targets` 鐢熸垚閾炬锛沗chain_delay_ms` 褰卞搷鏃跺簭锛沗damage_falloff_per_chain` 褰卞搷鍚庣画浼ゅ锛沗damage_type = lightning`锛沝amage 浜嬩欢鍚庢墸琛€锛沨it_vfx / floating_text 涓?damage 瀵归綈銆?
鎺ㄨ崘楠岃瘉鍛戒护锛歚python -m unittest tests.test_skill_runtime tests.test_skill_effects tests.test_combat`銆?
- [x] 5.1 灏?`chain` 鍔犲叆 SkillRuntime 閫氱敤 behavior template 鍒嗗彂銆?- [x] 5.2 瀹炵幇鏈€杩戞晫浜哄垵濮嬬洰鏍囬€夋嫨銆?- [x] 5.3 瀹炵幇 `nearest_not_hit` 鍚庣画鐩爣閫夋嫨鍜岄粯璁や笉閲嶅鍛戒腑銆?- [x] 5.4 瀹炵幇 `chain_radius` 璺濈杩囨护銆?- [x] 5.5 瀹炵幇 `chain_count` 鏈€澶ч摼娈甸檺鍒躲€?- [x] 5.6 瀹炵幇 `max_targets` 鏈€澶у懡涓洰鏍囬檺鍒躲€?- [x] 5.7 杈撳嚭 `cast_start` 鍜屽娈?`chain_segment`銆?- [x] 5.8 `chain_segment.payload` 杈撳嚭 `segment_index`銆乣from_target`銆乣to_target`銆乣start_position`銆乣end_position`銆乣chain_radius`銆乣chain_delay_ms`銆乣damage_scale`銆乣vfx_key`銆?- [x] 5.9 瀹炵幇 `chain_delay_ms` 閾炬鏃跺簭锛岀姝?cast_start 绔嬪嵆鎵归噺鎵ｈ銆?- [x] 5.10 閫氳繃 `damage` 浜嬩欢鎵ｈ锛屽苟杈撳嚭 `damage_type = lightning`銆?- [x] 5.11 瀹炵幇 `damage_falloff_per_chain` 鍚庣画閾炬浼ゅ琛板噺銆?- [x] 5.12 杈撳嚭 `hit_vfx` 鍜?`floating_text`锛屽苟涓庡搴?`damage` 瀵归綈銆?- [x] 5.13 娣诲姞 Runtime 娴嬭瘯瑕嗙洊閾炬瀛樺湪銆佽捣鐐?缁堢偣銆佹渶杩戠洰鏍囥€佸鐩爣鍛戒腑銆佸崐寰勫涓嶅懡涓€侀粯璁や笉閲嶅銆侀摼娈甸檺鍒躲€佺洰鏍囬檺鍒躲€佸欢杩熴€佷激瀹宠“鍑忓拰 modifier 鏁堟灉銆?
## 6. Phase 5: WebApp 娑堣垂 `chain` SkillEvent

鐩爣锛氳 WebApp 鏍规嵁鐪熷疄 `chain_segment`銆乣damage`銆乣hit_vfx` 鍜?`floating_text` 娓叉煋杩為攣闂數銆?
鍏佽淇敼鑼冨洿锛歚webapp/App.tsx`銆乣webapp/styles.css`銆乣webapp/smoke-test.mjs`銆乣tools/webapp_server.py` 涓繀瑕佷簨浠舵毚闇查€昏緫銆?
绂佹瓒婄晫浜嬮」锛氫笉寰楅€氳繃 `behavior_type`銆乣visual_effect`銆乣skill_lightning_chain`銆乣active_lightning_chain`銆乻kill id 鎴?VFX key 鐚滄祴琛屼负锛涗笉寰椾娇鐢ㄩ潤鎬佸亣浜嬩欢锛涗笉寰楁仮澶嶉殢鏈鸿瘝缂€ UI銆?
楠屾敹鏍囧噯锛歐ebApp 娓叉煋杩炵画鐢靛姬鐨勮捣鐐广€佺粓鐐广€侀『搴忋€佹椂闂村拰 VFX 鍧囨潵鑷?`chain_segment`锛涗激瀹炽€佸懡涓壒鏁堝拰娴瓧鏉ヨ嚜瀵瑰簲浜嬩欢锛涚帺瀹跺彲瑙佹枃鏈负涓枃銆?
鎺ㄨ崘楠岃瘉鍛戒护锛歚cmd /c npm run build`銆乣cmd /c npm test`銆?
- [x] 6.1 鍦?WebApp SkillEvent 娑堣垂璺緞鏀寔 `chain_segment`銆?- [x] 6.2 鏍规嵁 `chain_segment.payload.start_position` 鍜?`end_position` 娓叉煋閾炬鐢靛姬銆?- [x] 6.3 鏍规嵁 `segment_index` 鍜屼簨浠舵椂闂存樉绀洪摼娈甸『搴忎笌鏃跺簭銆?- [x] 6.4 淇濇寔 `damage`銆乣hit_vfx`銆乣floating_text` 鐢卞搴斾簨浠堕┍鍔ㄣ€?- [x] 6.5 娣诲姞 smoke test锛岃瘉鏄?WebApp 涓嶆牴鎹?skill id銆佹棫妯℃澘 id銆乥ehavior type銆乿isual effect 鎴?VFX key 鐚滄祴杩為攣琛屼负銆?
## 7. Phase 6: Skill Test Arena 鎺ュ叆杩為攣闂數

鐩爣锛氭敮鎸侀€夋嫨骞惰繍琛?`active_lightning_chain`锛岄獙璇佺湡瀹炶繛閿佹晥鏋溿€?
鍏佽淇敼鑼冨洿锛歚src/liufang/web_api.py`銆乣src/liufang/skill_test_report.py`銆乣tools/webapp_server.py`銆乣tests/test_skill_test_report.py`銆佺浉鍏虫祴璇曞満鏅暟鎹€?
绂佹瓒婄晫浜嬮」锛氫笉寰楀啓鐢熶骇搴撳瓨銆佸疂鐭冲疄渚嬫垨姝ｅ紡鎺夎惤鏁版嵁锛涗笉寰楄縼绉诲叾浠栨妧鑳斤紱涓嶅緱浣跨敤闈欐€佸亣浜嬩欢銆?
楠屾敹鏍囧噯锛氬崟浣撴湪妗┿€佸瘑闆嗗皬鎬€佷笁鐩爣妯帓鍦烘櫙鍙繍琛岋紱鑳介獙璇佸垵濮嬬洰鏍囥€佸悗缁洰鏍囥€侀摼鍗婂緞銆侀摼娆℃暟銆佷笉閲嶅鍛戒腑銆侀摼娈靛欢杩熴€佷激瀹宠“鍑忋€乨amage 鎵ｈ銆乂FX/娴瓧瀵归綈鍜?modifier 娴嬭瘯鏍堟晥鏋溿€?
鎺ㄨ崘楠岃瘉鍛戒护锛歚python -m unittest tests.test_skill_test_report tests.test_skill_runtime`銆乣python tools\generate_skill_test_report.py --skill active_lightning_chain --scenario dense_pack`銆?
- [x] 7.1 鍦?Skill Test Arena 鎶€鑳介€夋嫨涓帴鍏?`active_lightning_chain`銆?- [x] 7.2 澧炲姞鎴栧鐢ㄥ崟浣撴湪妗╁満鏅獙璇佸熀纭€鏃跺簭銆?- [x] 7.3 澧炲姞鎴栧鐢ㄥ瘑闆嗗皬鎬満鏅獙璇佸鐩爣璺宠穬銆?- [x] 7.4 澧炲姞鎴栧鐢ㄤ笁鐩爣妯帓鍦烘櫙楠岃瘉閾惧崐寰勫拰閾炬杈圭晫銆?- [x] 7.5 楠岃瘉 `chain_count` 淇敼鍚庨摼娈垫暟閲忓彉鍖栥€?- [x] 7.6 楠岃瘉 `chain_radius` 淇敼鍚庡彲璺宠穬鐩爣鑼冨洿鍙樺寲銆?- [x] 7.7 楠岃瘉 `chain_delay_ms` 淇敼鍚庨摼娈垫椂闂撮棿闅斿彉鍖栥€?- [x] 7.8 楠岃瘉 `damage_falloff_per_chain` 淇敼鍚庡悗缁摼娈典激瀹冲彉鍖栥€?- [x] 7.9 楠岃瘉 Modifier 娴嬭瘯鏍堝奖鍝嶆渶缁堜激瀹虫垨杩為攣鍙傛暟銆?
## 8. Phase 7: SkillEvent 鏃堕棿绾夸笌 AI 鑷祴鎶ュ憡鎺ュ叆杩為攣闂數

鐩爣锛氭椂闂寸嚎鏄剧ず `active_lightning_chain` 鐪熷疄浜嬩欢锛孉I 鑷祴鎶ュ憡鍩轰簬鐪熷疄缁撴灉杈撳嚭涓枃缁撹銆?
鍏佽淇敼鑼冨洿锛歚src/liufang/skill_test_report.py`銆乣tools/generate_skill_test_report.py`銆乣src/liufang/web_api.py`銆乣webapp/App.tsx` 涓椂闂寸嚎灞曠ず銆乣tests/test_skill_test_report.py`銆乣webapp/smoke-test.mjs`銆?
绂佹瓒婄晫浜嬮」锛氫笉寰椾娇鐢ㄩ潤鎬佸亣浜嬩欢锛涗笉寰楃敤 skill id 鐚滆涓猴紱涓嶅緱杈撳嚭鑻辨枃鐜╁鍙鏂囨銆?
楠屾敹鏍囧噯锛氭椂闂寸嚎鏄剧ず `cast_start`銆佸娈?`chain_segment`銆佸娈?`damage`銆乣hit_vfx`銆乣floating_text`銆乣cooldown_update`锛汚I 鎶ュ憡妫€鏌ラ摼娈点€佸鐩爣銆佷笉閲嶅銆佹椂搴忋€佸弬鏁板彉鍖栧拰 lightning damage type锛屽苟杈撳嚭涓枃閫氳繃 / 閮ㄥ垎閫氳繃 / 涓嶉€氳繃銆佷笉涓€鑷撮」鍜屽缓璁慨澶嶉」銆?
鎺ㄨ崘楠岃瘉鍛戒护锛歚python -m unittest tests.test_skill_test_report`銆乣python tools\generate_skill_test_report.py --skill active_lightning_chain --scenario dense_pack`銆乣cmd /c npm test`銆?
- [x] 8.1 鏃堕棿绾挎敮鎸佹樉绀?`chain_segment` 澶氭浜嬩欢銆?- [x] 8.2 鏃堕棿绾挎樉绀鸿姹傚瓧娈碉細`timestamp_ms`銆乣delay_ms`銆乣duration_ms`銆乣source_entity`銆乣target_entity`銆乣amount`銆乣damage_type`銆乣vfx_key`銆乣reason_key`銆乣payload`銆?- [x] 8.3 AI 鎶ュ憡鏀寔 `python tools\generate_skill_test_report.py --skill active_lightning_chain --scenario dense_pack`銆?- [x] 8.4 AI 鎶ュ憡妫€鏌ユ槸鍚﹀瓨鍦?`chain_segment` 鍜屽娈?`chain_segment`銆?- [x] 8.5 AI 鎶ュ憡妫€鏌?`damage`銆乣hit_vfx`銆乣floating_text`銆?- [x] 8.6 AI 鎶ュ憡妫€鏌?damage 涓嶆棭浜庡搴?`chain_segment`锛屼笖 cast_start 涓嶇洿鎺ユ墸琛€銆?- [x] 8.7 AI 鎶ュ憡妫€鏌ュ鐩爣鍛戒腑銆侀粯璁や笉閲嶅鍛戒腑鍜屽崐寰勫涓嶅懡涓€?- [x] 8.8 AI 鎶ュ憡妫€鏌?`chain_count`銆乣chain_radius`銆乣chain_delay_ms`銆乣damage_falloff_per_chain` 淇敼鍚庣殑鐪熷疄缁撴灉鍙樺寲銆?- [x] 8.9 AI 鎶ュ憡妫€鏌?`damage_type = lightning`銆?- [x] 8.10 AI 鎶ュ憡杈撳嚭涓枃缁撹銆佷笉涓€鑷撮」鍜屽缓璁慨澶嶉」銆?
## 9. Phase 8: 楠岃瘉涓庡洖褰?
鐩爣锛氬畬鎴愰厤缃€丳ython銆丱penSpec銆乄ebApp 鍜?AI 鎶ュ憡楠岃瘉锛岀‘璁よ縼绉昏寖鍥存湭瓒婄晫銆?
鍏佽淇敼鑼冨洿锛氫粎鍏佽涓轰慨澶嶆湰 change 楠岃瘉澶辫触鑰屼慨鏀规湰 change 鍏佽鑼冨洿鍐呮枃浠讹紱鍙洿鏂?`openspec/changes/migrate-active-lightning-chain-to-chain/tasks.md` 鍕鹃€夊畬鎴愰」銆?
绂佹瓒婄晫浜嬮」锛氫笉寰楄縼绉?`active_lava_orb`銆乣active_fungal_petards`锛涗笉寰椾慨鏀规寮忔帀钀姐€佸簱瀛樸€佸疂鐭崇洏锛涗笉寰楁仮澶嶉殢鏈鸿瘝缂€ UI 鎴栫敓鎴愶紱涓嶅緱鐮村潖宸茶縼绉绘妧鑳借兘鍔涳紱涓嶅緱寮曞叆鑻辨枃鐜╁鍙鏂囨銆?
楠屾敹鏍囧噯锛氶厤缃牎楠屻€丳ython 鍗曟祴銆丱penSpec strict validate銆乶pm build銆乶pm test銆佽繛閿侀棯鐢?AI 鎶ュ憡鍏ㄩ儴杩愯锛沗active_fire_bolt`銆乣active_ice_shards`銆乣active_penetrating_shot`銆乣active_frost_nova`銆乣active_puncture` 鏃犲洖褰掞紱鏈縼绉绘妧鑳戒粛鏈縼绉汇€?
鎺ㄨ崘楠岃瘉鍛戒护锛歚python tools\validate_v1_configs.py`銆乣python -m unittest discover tests`銆乣cmd /c openspec validate migrate-active-lightning-chain-to-chain --strict`銆乣cmd /c npm run build`銆乣cmd /c npm test`銆乣python tools\generate_skill_test_report.py --skill active_lightning_chain --scenario dense_pack`銆?
- [x] 9.1 杩愯 `python tools\validate_v1_configs.py`銆?- [x] 9.2 杩愯 `python -m unittest discover tests`銆?- [x] 9.3 杩愯 `cmd /c openspec validate migrate-active-lightning-chain-to-chain --strict`銆?- [x] 9.4 杩愯 `cmd /c npm run build`銆?- [x] 9.5 杩愯 `cmd /c npm test`銆?- [x] 9.6 杩愯 `python tools\generate_skill_test_report.py --skill active_lightning_chain --scenario dense_pack`銆?- [x] 9.7 纭 `active_fire_bolt`銆乣active_ice_shards`銆乣active_penetrating_shot`銆乣active_frost_nova`銆乣active_puncture` 鏃犲洖褰掋€?- [x] 9.8 纭 `active_lava_orb`銆乣active_fungal_petards` 鍜屽叾浠栨湭杩佺Щ鎶€鑳戒粛鏈縼绉汇€?- [x] 9.9 纭娌℃湁鎭㈠闅忔満璇嶇紑 UI 鎴栭殢鏈鸿瘝缂€鐢熸垚銆?- [x] 9.10 纭娌℃湁鏂板鑻辨枃鐜╁鍙鏂囨銆?
