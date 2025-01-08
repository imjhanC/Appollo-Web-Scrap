from seleniumbase import SB

with SB(uc=True, incognito=True, test=True) as sb:
    sb.driver.uc_open_with_reconnect("https://pixelscan.net/", 10)
    sb.remove_elements("jdiv")  # Remove chat widgets
    sb.highlight("span.text-success", loops=8)
    sb.highlight(".bot-detection-context", loops=10, scroll=False)
    sb.sleep(2)