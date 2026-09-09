# Enjoy the End — Update Log

## 2026-09-09 — Prototype 0.12: character wording & mobile focus

### Character creation
- Replaced “性别” with “外表气质”: 男性化 / 中性 / 女性化.
- Replaced “体重 / 体型” with “体格”: 纤细 / 匀称 / 壮实.
- Rewrote mirror preview generation so it produces natural prose instead of mechanically repeating values such as “中等”.
- Added a reserved “身体特征” section for 胸部轮廓、男性身体特征、女性身体特征.
- Reserved body-feature data does not enter ordinary mirror or outward-appearance descriptions.

### Mobile play layout
- Mobile gameplay now keeps the immediate page focused on 房间描述、身体与心理状态、近期记录.
- 房间描述 now includes a concise weather/environment line and is prepared to include visible NPC activity in the same area.
- 房间互动、行动、家中储备、容器、天气预报、外出装备、世界状况 are moved behind dedicated view buttons on narrow screens.
- Secondary views open as full-screen mobile panels and can be closed back to the core gameplay view.

### Deployment repair
- Repaired the invalid GitHub Actions YAML that caused runs #10 and #11 to fail before jobs started.
- Moved HTML transformation logic into a standalone build_patch.py file, keeping the workflow itself small and valid.
- Deployment continues to build from the existing compressed prototype source and publishes through GitHub Pages.
