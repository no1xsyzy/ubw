from bliveshield.BiliLiveAntiShield import BiliLiveAntiShield
from bliveshield.BiliLiveShieldWords import rules, words

shield = BiliLiveAntiShield(rules, words, "·")
while x := input("> ").strip():
    result = shield.deal(x)
    print(result)
