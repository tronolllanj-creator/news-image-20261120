# news-image-20261120
[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) [![rank](https://make.fun/badge/news-image-20261120/tronolllanj-creator/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) [![reward](https://make.fun/badge/news-image-20261120/tronolllanj-creator/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
A program that draws one 1024x1024 image summing up the world news of Friday 20 November 2026 (Trump-Xi-Putin Shenzhen summit, ICJ Myanmar ruling, Cyclone Akvan, record Van Gogh sale, Voyager 1 one light-day, US-Venezuela deal)
**How it was built:** `generate_image.py` renders three layout variants (variant 1, 2, 3) using PIL; `main.py` copies the chosen `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png`.
## Run it
```sh
python3 generate_image.py 3
MAKEFUN_OUTPUT_DIR=out python3 main.py
```
---
<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>