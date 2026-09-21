import sys

MOD = 26


def only_letters(text):
    return ''.join(ch for ch in text if ch.isalpha())


def clean_key(text):
    return only_letters(text).upper()


def count_letters(text):
    return sum(1 for ch in text if ch.isalpha())


def vigenere_transform(text, key, mode):
    key_numbers = [ord(k) - ord('A') for k in key]
    jumlah_kunci = len(key_numbers)
    hasil = []
    indeks_kunci = 0
    for ch in text:
        if ch.isalpha():
            huruf_besar = ch.isupper()
            basis = ord('A') if huruf_besar else ord('a')
            nilai_teks = ord(ch.upper()) - ord('A')
            nilai_kunci = key_numbers[indeks_kunci % jumlah_kunci]
            if mode == 'encrypt':
                nilai_hasil = (nilai_teks + nilai_kunci) % MOD
            else:
                nilai_hasil = (nilai_teks - nilai_kunci) % MOD
            hasil.append(chr(nilai_hasil + basis))
            indeks_kunci += 1
        else:
            hasil.append(ch)
    return ''.join(hasil)


def process_encrypt(data):
    plaintext = data['plaintext']
    key = data['key']
    ciphertext = vigenere_transform(plaintext, key, mode='encrypt')
    return {'plaintext': plaintext, 'key': key, 'ciphertext': ciphertext}


def process_decrypt(data):
    ciphertext = data['ciphertext']
    key = data['key']
    plaintext = vigenere_transform(ciphertext, key, mode='decrypt')
    return {'ciphertext': ciphertext, 'key': key, 'plaintext': plaintext}


def process_all(mode, data):
    try:
        if mode == '1':
            return process_encrypt(data)
        elif mode == '2':
            return process_decrypt(data)
    except Exception as e:
        display_error(f"Terjadi kesalahan tak terduga saat memproses data ({e}). "
                       f"Silakan periksa kembali input Anda dan coba lagi.")
        return None


def display_error(pesan):
    print(f"\n[ERROR] {pesan}")


def display_warning(pesan):
    print(f"\n[PERINGATAN] {pesan}")


def display_info(pesan):
    print(f"[INFO] {pesan}")


def display_menu():
    print("\n" + "=" * 60)
    print(" PROGRAM VIGENERE CIPHER ".center(60, "="))
    print("=" * 60)
    print(" 1. Enkripsi teks")
    print(" 2. Dekripsi teks")
    print(" 3. Keluar dari program")
    print("=" * 60)


def display_welcome():
    print("\nSelamat datang di Program Vigenere Cipher (kunci berulang, modulo 26 / A-Z).")
    print("Karakter non-huruf pada teks akan dipertahankan apa adanya di hasil akhir.")


def show_output(mode, result_data):
    if result_data is None:
        return
    if mode == '1':
        print("\n--- HASIL ENKRIPSI ---")
        display_info(f"Kunci yang digunakan : {result_data['key']}")
        print(f"Plaintext  : {result_data['plaintext']}")
        print(f"Ciphertext : {result_data['ciphertext']}")
    elif mode == '2':
        print("\n--- HASIL DEKRIPSI ---")
        display_info(f"Kunci yang digunakan : {result_data['key']}")
        print(f"Ciphertext : {result_data['ciphertext']}")
        print(f"Plaintext  : {result_data['plaintext']}")


def input_menu_choice():
    while True:
        pilihan = input("Pilih menu (1-3): ").strip()
        if pilihan in ('1', '2', '3'):
            return pilihan
        display_error("Pilihan tidak dikenali! Harap masukkan angka 1, 2, atau 3 sesuai menu di atas.")


def input_plain_or_cipher_text(label):
    while True:
        mentah = input(f"Masukkan {label}: ")
        if mentah == '':
            display_error(f"{label.capitalize()} tidak boleh kosong! Silakan masukkan kembali.")
            continue
        if count_letters(mentah) == 0:
            display_error(
                f"{label.capitalize()} harus mengandung minimal satu huruf (A-Z/a-z) "
                f"agar dapat diproses! Silakan masukkan kembali."
            )
            continue
        return mentah


def input_key():
    while True:
        mentah = input("Masukkan kunci (key): ")
        if mentah.strip() == '':
            display_error("Kunci tidak boleh kosong! Silakan masukkan kembali.")
            continue
        bersih = clean_key(mentah)
        if bersih == '':
            display_error(
                "Kunci harus mengandung minimal satu huruf (A-Z)! Karakter non-huruf "
                "tidak dapat dijadikan kunci. Silakan masukkan kembali."
            )
            continue
        if bersih != mentah.strip().upper():
            display_info(f"Karakter non-huruf pada kunci telah diabaikan. Kunci yang digunakan: {bersih}")
        return bersih


def input_yes_no(pertanyaan):
    while True:
        mentah = input(f"{pertanyaan} (y/n): ").strip().lower()
        if mentah in ('y', 'yes', 'ya'):
            return True
        if mentah in ('n', 'no', 'tidak'):
            return False
        display_error("Jawaban tidak dikenali! Harap masukkan 'y' untuk ya atau 'n' untuk tidak.")


def get_all_inputs(mode):
    data = {}
    if mode == '1':
        plaintext = input_plain_or_cipher_text("teks asli (plaintext) yang ingin dienkripsi")
        key = input_key()
        data.update(plaintext=plaintext, key=key)
    elif mode == '2':
        ciphertext = input_plain_or_cipher_text("teks sandi (ciphertext) yang ingin didekripsi")
        key = input_key()
        data.update(ciphertext=ciphertext, key=key)
    return data


def run_vigenere_program():
    display_welcome()
    while True:
        display_menu()
        mode = input_menu_choice()
        if mode == '3':
            print("\nTerima kasih telah menggunakan Program Vigenere Cipher. Sampai jumpa!")
            break
        data = get_all_inputs(mode)
        hasil = process_all(mode, data)
        show_output(mode, hasil)
        if not input_yes_no("\nApakah Anda ingin melakukan operasi lain?"):
            print("\nTerima kasih telah menggunakan Program Vigenere Cipher. Sampai jumpa!")
            break


if __name__ == "__main__":
    try:
        run_vigenere_program()
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan paksa oleh pengguna (Ctrl+C). Sampai jumpa!")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nTerjadi kesalahan fatal pada program: {e}")
        print("Program akan ditutup. Mohon laporkan masalah ini jika terus terjadi.")
        sys.exit(1)
