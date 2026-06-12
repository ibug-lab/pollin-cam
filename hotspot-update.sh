sudo nmcli connection add \
  type wifi \
  con-name "jhemberg_iphone" \
  ifname wlan0 \
  ssid "jhemberg_iphone"

sudo nmcli connection modify "jhemberg_iphone" \
  wifi-sec.key-mgmt wpa-psk \
  wifi-sec.psk "YourPassword"
