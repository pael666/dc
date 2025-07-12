#!/usr/bin/env python3
# Discord Auto-Message & Delete Script
# Use At Your Own Risk

import requests
import random
import sys
import yaml
import time

class Discord:
    """
    Class untuk berinteraksi dengan Discord API v9
    """
    def __init__(self, token):
        self.base = "https://discord.com/api/v9"
        self.auth = {'authorization': token}

    def getMe(self):
        try:
            res = requests.get(self.base + "/users/@me", headers=self.auth)
            res.raise_for_status() # Akan error jika status code bukan 2xx
            return res.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user details: {e}")
            return None

    def sendMessage(self, channel_id, text):
        try:
            payload = {'content': text}
            res = requests.post(f"{self.base}/channels/{channel_id}/messages", headers=self.auth, json=payload)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")
            return None

    def deleteMessage(self, channel_id, message_id):
        try:
            res = requests.delete(f"{self.base}/channels/{channel_id}/messages/{message_id}", headers=self.auth)
            res.raise_for_status()
            # Delete request tidak mengembalikan body jika berhasil, jadi kita return status code
            return res.status_code
        except requests.exceptions.RequestException as e:
            print(f"Error deleting message: {e}")
            return None

def main():
    """
    Fungsi utama untuk menjalankan bot
    """
    try:
        with open('config.yaml', 'r') as cfg_file:
            conf = yaml.safe_load(cfg_file)
    except FileNotFoundError:
        print("[FATAL ERROR] File 'config.yaml' tidak ditemukan! Silakan buat file tersebut.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"[FATAL ERROR] Gagal membaca config.yaml: {e}")
        sys.exit(1)

    # Validasi konfigurasi
    if not conf.get('BOT_TOKEN'):
        print("[!] Tolong masukkan BOT_TOKEN di config.yaml!")
        sys.exit(1)
    if not conf.get('CHANNEL_ID'):
        print("[!] Tolong masukkan CHANNEL_ID di config.yaml!")
        sys.exit(1)

    delay = conf.get('DELAY', 65)
    delete_delay = conf.get('DELETE_DELAY', 5)
    messages = conf.get('MESSAGES', ["Pesan default."])

    while True:
        for token in conf['BOT_TOKEN']:
            try:
                bot = Discord(token)
                me_info = bot.getMe()

                if not me_info or 'username' not in me_info:
                    print(f"[ERROR] Token {token[:15]}... tidak valid atau gagal login.")
                    continue

                me = f"{me_info['username']}#{me_info['discriminator']}"
                print(f"[{me}] Login berhasil.")

                for channel_id in conf['CHANNEL_ID']:
                    # Pilih pesan acak dari daftar
                    message_to_send = random.choice(messages)
                    
                    print(f"[{me}] Mengirim '{message_to_send}' ke channel {channel_id}...")
                    sent_message = bot.sendMessage(channel_id, message_to_send)

                    if sent_message and 'id' in sent_message:
                        print(f"[{me}] Pesan terkirim (ID: {sent_message['id']}). Menunggu {delete_delay} detik untuk menghapus...")
                        
                        # Tunggu sejenak sebelum menghapus
                        time.sleep(delete_delay)
                        
                        status = bot.deleteMessage(channel_id, sent_message['id'])
                        if status == 204: # 204 No Content adalah status sukses untuk delete
                            print(f"[{me}] Pesan {sent_message['id']} berhasil dihapus.")
                        else:
                            print(f"[{me}] Gagal menghapus pesan {sent_message['id']}. Status: {status}")
                    else:
                        print(f"[{me}] Gagal mengirim pesan ke channel {channel_id}.")

            except Exception as e:
                print(f"[ERROR LOOP] Terjadi kesalahan: {e}")
        
        print(f"------ SIKLUS SELESAI. Jeda selama {delay} detik ------")
        time.sleep(delay)

if __name__ == '__main__':
    main()