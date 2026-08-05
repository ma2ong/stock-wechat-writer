#!/usr/bin/env python3
from __future__ import annotations

import unittest

import pre_publish_check


BASE_ARTICLE = """# 测试标题

明天看什么：看存储主线是否继续放量。

兆易创新（603986）今天放量上涨，成交额120亿。
大普微-UW（301666）今天20cm涨停，成交额45.7亿。

如果存储方向继续放量并站稳5日线，可以继续观察；若跌破今日低点则回避。

数据来源：东方财富、同花顺。风险提示：本文不构成投资建议。
"""


class PrePublishCheckTest(unittest.TestCase):
    def test_mismatched_stock_name_fails(self) -> None:
        text = BASE_ARTICLE.replace("大普微-UW（301666）", "大普微（688469）")
        failures, _ = pre_publish_check.check_article(text)
        self.assertTrue(any("股票代码-名称不匹配" in item for item in failures))

    def test_unverified_stock_name_fails_by_default(self) -> None:
        original = pre_publish_check.fetch_eastmoney_names
        pre_publish_check.fetch_eastmoney_names = lambda codes: {}
        try:
            failures, _ = pre_publish_check.check_article(BASE_ARTICLE)
        finally:
            pre_publish_check.fetch_eastmoney_names = original
        self.assertTrue(any("未能从东方财富/本地缓存校验股票代码" in item for item in failures))

    def test_unverified_stock_name_can_be_allowed_after_manual_check(self) -> None:
        original = pre_publish_check.fetch_eastmoney_names
        pre_publish_check.fetch_eastmoney_names = lambda codes: {}
        try:
            failures, warnings = pre_publish_check.check_article(
                BASE_ARTICLE,
                allow_unverified_stock_names=True,
            )
        finally:
            pre_publish_check.fetch_eastmoney_names = original
        self.assertFalse(any("未能从东方财富/本地缓存校验股票代码" in item for item in failures))
        self.assertTrue(any("未能从东方财富/本地缓存校验股票代码" in item for item in warnings))

    def test_public_article_leak_fails(self) -> None:
        text = BASE_ARTICLE + "\n你给我的截图里，东方财富截图显示这个板块最强。\n"
        failures, _ = pre_publish_check.check_article(text, verify_stock_names=False)
        self.assertTrue(any("过程话或截图来源表述" in item for item in failures))

    def test_sector_scoreboard_list_warns(self) -> None:
        text = BASE_ARTICLE + (
            "\n电力涨3.43%，半导体涨2.96%，IT服务涨2.79%，公用事业涨2.78%，"
            "软件开发涨2.34%，元件涨2.18%，MLCC涨6.21%，MLOps涨3.88%。\n"
        )
        _, warnings = pre_publish_check.check_article(text, verify_stock_names=False)
        self.assertTrue(any("涨幅榜当文章目录" in item for item in warnings))

    def test_pivot_sentence_variants_warn(self) -> None:
        variants = {
            "并非X而是Y": "并非利空出尽，而是还在消化。",
            "不在于X而在于Y": "关键不在于点位，而在于量能。",
            "与其说X不如说Y": "与其说是反弹，不如说是超跌修复。",
            "不只X还/也Y": "不只是政策在推，外资也在买。",
            "看似X实则Y": "看似普涨，实则只有三个板块在动。",
        }
        for label, sentence in variants.items():
            with self.subTest(label=label):
                _, warnings = pre_publish_check.check_article(
                    BASE_ARTICLE + "\n" + sentence + "\n",
                    verify_stock_names=False,
                )
                self.assertTrue(
                    any(f"固定句式风险：{label}" in item for item in warnings),
                    f"{label} 未被检出",
                )

    def test_repeated_paragraph_opener_warns(self) -> None:
        text = BASE_ARTICLE + (
            "\n其实今天的量能没跟上。\n\n其实主线也换了。\n\n"
            "其实外资是净卖出的。\n\n其实明天要看能不能补量。\n"
        )
        _, warnings = pre_publish_check.check_article(text, verify_stock_names=False)
        self.assertTrue(any("段落开场重复" in item for item in warnings))

    def test_mixed_metaphor_fields_warn(self) -> None:
        text = BASE_ARTICLE + (
            "\n这条赛道已经开始降温，几家公司的地基没打好，弹药也快耗尽了。\n"
        )
        _, warnings = pre_publish_check.check_article(text, verify_stock_names=False)
        self.assertTrue(any("套借喻" in item for item in warnings))

    def test_clean_article_has_no_new_shape_warnings(self) -> None:
        _, warnings = pre_publish_check.check_article(
            BASE_ARTICLE, verify_stock_names=False
        )
        for noise in ("固定句式风险", "段落开场重复", "套借喻"):
            self.assertFalse(
                any(noise in item for item in warnings),
                f"干净稿被误报：{noise}",
            )


if __name__ == "__main__":
    unittest.main()
