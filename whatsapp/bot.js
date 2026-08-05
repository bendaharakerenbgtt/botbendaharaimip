const { makeWASocket, useMultiFileAuthState, DisconnectReason, Browsers } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const pino = require('pino');
const fs = require('fs');

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('baileys_auth_info');

    const sock = makeWASocket({
        auth: state,
        logger: pino({ level: 'silent' }),
        browser: Browsers.macOS('Desktop'),
        syncFullHistory: false,
        markOnlineOnConnect: false,
        generateHighQualityLinkPreview: true
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            console.log('\nScan QR Code di bawah ini menggunakan WhatsApp HP kamu:\n');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'close') {
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
            
            console.log(`Koneksi terputus (Status Code: ${statusCode}). Mencoba menghubungkan ulang...`);

            if (!shouldReconnect) {
                console.log('Session resmi di-logout dari HP. Menghapus sesi lama untuk QR baru...');
                try {
                    fs.rmSync('baileys_auth_info', { recursive: true, force: true });
                } catch (e) {}
            } else {
                console.log('Sesi tersimpan (baileys_auth_info) AMAN & TERSIMPAN. Bot akan otomatis login kembali tanpa perlu scan QR!');
            }

            // Reconnect otomatis dalam 3 detik menggunakan sesi tersimpan
            setTimeout(connectToWhatsApp, 3000);
        } else if (connection === 'open') {
            console.log('✅ Bot WhatsApp (Baileys) terhubung dan siap digunakan!');
        }
    });

    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return;

        for (const msg of messages) {
            if (!msg.message || msg.key.fromMe) continue;

            const text = msg.message.conversation ||
                         msg.message.extendedTextMessage?.text ||
                         '';

            if (!text) continue;

            const from = msg.key.remoteJid;
            console.log(`[Pesan Masuk dari ${from}]: ${text}`);

            try {
                const res = await fetch('http://127.0.0.1:5000/bot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });

                const data = await res.json();

                if (data && data.reply) {
                    // Simulasi ketikan manusia (human-like typing) 1.5 detik agar anti-spam WA
                    await sock.sendPresenceUpdate('composing', from);
                    await new Promise(r => setTimeout(r, 1500));
                    await sock.sendPresenceUpdate('paused', from);

                    await sock.sendMessage(from, { text: data.reply }, { quoted: msg });
                }
            } catch (error) {
                console.error('Error menghubungkan ke Flask API:', error.message);
            }
        }
    });
}

connectToWhatsApp();