# Strava Receipts

Automatically print your most recent Strava activity to a receipt printer.

Developed and tested using a Raspberry Pi Zero W and Epson TM-T88IV printer. 

Inspired by: [https://github.com/aschmelyun/github-receipts](https://github.com/aschmelyun/github-receipts)

## Instructions

### 1. Hardware Permissions
By default, Linux restricts USB write access to the root user. To allow this script to communicate with the printer without using `sudo` every time or re-applying permissions after each reboot, you need to create a permanent udev rule.

Find your printer's vendor and product IDs by running `lsusb`

Look for output like: `Bus 001 Device 004: ID 04b8:0202 Seiko Epson Corp.`

Vendor ID: `04b8` 

Product ID: `0202`

Create and apply the udev rule (replace `VENDOR_ID` and `PRODUCT_ID` with your values):
```bash
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="VENDOR_ID", ATTR{idProduct}=="PRODUCT_ID", MODE="0666"' | sudo tee /etc/udev/rules.d/99-escpos.rules && \
sudo udevadm control --reload-rules && \
sudo udevadm trigger 
```

You may need to reboot for the changes to take effect:
```bash
sudo reboot
```

### 2. Clone Repo & Install Dependencies
```bash
git clone https://github.com/bencarlstrom/strava-receipts.git && \
cd strava-receipts && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt
```

### 3. Strava API Credentials

1. Register your app at https://www.strava.com/settings/api
   - Set the **domain** and **authorization callback** to `localhost`

2. Get your initial tokens by building this authorization URL (replace `YOUR_CLIENT_ID`):
```
   https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all
```

3. Open the URL in a browser and click **authorize** when prompted

4. You'll be redirected to a URL like `http://localhost/exchange_token?code=AUTHORIZATION_CODE`
   - Copy the `AUTHORIZATION_CODE` value from the URL

5. Exchange the code for tokens (replace placeholders):
```bash
   curl -X POST https://www.strava.com/api/v3/oauth/token \
     -d client_id=YOUR_CLIENT_ID \
     -d client_secret=YOUR_CLIENT_SECRET \
     -d code=AUTHORIZATION_CODE \
     -d grant_type=authorization_code
```

6. Save the `refresh_token` and `access_token` from the JSON response

### 4. Configuration

1. Copy the example files:
```bash
   cp .env.example .env && \
   cp config.py.example config.py
```

2. Add your Strava credentials to the `.env`
   
   - You can find these here: [https://www.strava.com/settings/api](https://www.strava.com/settings/api)

3. Add the printer's vendor and product IDs to your `config.py`

   - **Note**: Add the hex prefix `0x` to each ID. 

### 5. Run
```bash
python main.py
```

## Notes

- Access tokens are automatically refreshed and cached in `.token_cache`
- The refresh token in `.env` is expected to remain valid


