from flask import Flask, render_template, request
import nltk
import re
import string
import pandas as pd
import numpy as np
import time
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from fuzzywuzzy import fuzz, process
app = Flask(__name__, template_folder='html')

def preprocess(berita):
    factory = StopWordRemoverFactory()
    stopword = factory.create_stop_word_remover()

    # menghapus karakter yang tidak diinginkan (encoded char)
    berita = ''.join(b for b in berita if ord(b) < 128)
    
    # mengubah semua kata menjadi huruf kecil
    berita = berita.casefold()
    
    # menghapus angka
    berita = re.sub(r"\d+", "", berita)
    
    # menghapus tanda baca
    berita = berita.translate(str.maketrans("", "", string.punctuation))
    
    # menghapus spasi di awal dan akhir
    berita = berita.strip()
    
    # menghapus kata-kata yang memiliki informasi rendah dari sebuah teks
    stop = stopword.remove(berita)
    
    # tokenisasi kata
    tokenized_data = nltk.tokenize.word_tokenize(stop)
    
    return tokenized_data

# def calculate_hash(kata, p, m):
#     hash_value = 0
#     p_pow = 26

#     for word in kata:
#         for char in word:
#             hash_value = (hash_value + (ord(char) - ord('a') + 1) * p_pow) % m
#             p_pow = (p_pow * p) % m

#     return hash_value

# def rabin_karp_hash(kata, dataset_kata):
#     # p adalah bilangan prima untuk menghitung polinomial hash
#     p = 127
#     # m adalah bilangan prima yang dibuat cukup besar untuk menghindari tabrakan pada hash table
#     m = 2**127 - 1

#     result = []
#     hasil_dataset_kata_hash = []
#     x = len(dataset_kata)
#     y = len(kata)

#     kata_hash = hash(kata) % m

#     for i in range(x - y + 1):
#         for j in range(len(dataset_kata)):
#             substring_hash = hash(dataset_kata[j]) % m
#             # hasil_dataset_kata_hash.append(substring_hash)
#             if kata_hash == substring_hash:
#                 if kata == dataset_kata[j]:
#                     result.append(j)

#         if i < x - y:
#             p_pow = 26
#             for first_char in kata:
#                 kata_hash = (kata_hash + (ord(first_char) - ord('a') + 1) * p_pow) % m
#                 p_pow = (p_pow * p) % m

#     return result

# def rabin_karp_hash(kata):
#     # p adalah bilangan prima untuk menghitung polinomial hash
#     p = 127
#     # m adalah bilangan prima yang dibuat cukup besar untuk menghindari tabrakan pada hash table
#     m = 2**127 - 1

#     hash_value = 0
#     p_pow = 26
#     for char in kata:
#         hash_value = (hash_value + (ord(char) - ord('a') + 1) * p_pow) % m
#         p_pow = (p_pow * p) % m

#     return hash_value

def calculate_hash(kata, p, m):
    hash_value = 0
    p_pow = 26

    for char in kata:
        hash_value = (hash_value + (ord(char) - ord('a') + 1) * p_pow) % m
        p_pow = (p_pow * p) % m

    return hash_value

def rabin_karp(kata, dataset_kata_benar):
    p = 127  # prime number for calculating the hash
    m = 2 ** 127 - 1  # prime number to avoid collisions

    pattern_hash = calculate_hash(kata, p, m)
    idx = []
    words = []

    for i, string in enumerate(dataset_kata_benar):
        string_hash = calculate_hash(string, p, m)
        if string_hash == pattern_hash and string == kata:
            idx.append(i)
        else:
        # if string_hash != pattern_hash and string != kata:
            words.append(kata)

    return idx, words

def deteksi_kata_luluh(berita, list_kata_dasar, list_kata_benar):
    huruf_depan = ['s', 'k', 'p', 't']
    daftar_prefiks = ['me', 'pe']
    kluster = ['kh', 'kl', 'kn', 'kr', 'pl', 'pr', 'sk', 'sm', 'sp', 'sr', 'st', 'sw', 'sy', 'tr']
    awalan = ['mempe', 'mempen', 'mempem', 'mempeng', 'memper']

    # kata_benar_hash = []
    hasil = []
    hasil_salah = []

    flag = False
    # another_flag = False
    # for k in range(len(list_kata_benar)):
    #     kata_benar_hash.append(rabin_karp_hash(list_kata_benar[k]))

    for daftar_kata in berita:
        another_flag = False
        kata_dasar = stemmer.stem(daftar_kata)

        if daftar_kata == 'mengaji':
            kata_dasar = 'kaji'
        elif daftar_kata == 'mengkaji':
            continue

        if daftar_kata == 'pemasukan':
            kata_dasar = 'masuk'

        if daftar_kata == 'memperhatikan':
            kata_dasar = 'hati'

        if daftar_kata == 'memasuki':
            kata_dasar = 'masuk'
        elif daftar_kata == 'memasuk':
            kata_dasar = 'pasuk'

        if daftar_kata == 'mempunyai':
            kata_dasar = 'empunya'

        for x in range(len(awalan)):
            # cek apakah katanya memiliki 2 prefiks dan diikuti kata dasar di belakangnya
            if daftar_kata.startswith(awalan[x] + kata_dasar):
                another_flag = True
                # print(daftar_kata)
                break
            # if not daftar_kata.startswith(awalan[x] + kata_dasar):
            #     another_flag = False
            # else:
            #     print(daftar_kata)
            #     another_flag = True
            #     break

        if another_flag == False:

            # cek apakah katanya berimbuhan
            if len(daftar_kata) > len(kata_dasar):

                # cek apakah huruf depan kata berawalan s, p, k, t
                if kata_dasar[0] in huruf_depan:

                    # cek apakah kata dasarnya ada dalam dataset kata dasar
                    if kata_dasar in list_kata_dasar:

                        for i in range(len(daftar_prefiks)):
                                
                            # cek apakah katanya berawalan me- dan pe- 
                            # dan katanya bukan kata dasar yang berawalan me- dan pe- yang diakhiri dengan sufiks
                            if daftar_kata.startswith(daftar_prefiks[i]) and not daftar_kata.startswith(kata_dasar):

                                for j in range(len(kluster)):
                                    # cek apakah kata dasarnya berawalan dengan kluster
                                    if kata_dasar.startswith(kluster[j]):
                                        # kalau kata dasarnya berawalan dengan kluster
                                        # setting flag = True, kemudian break untuk menyatakan bahwa ditemukan kluster
                                        flag = True
                                        break
                                    else:
                                        # jika tidak ditemukan kluster, loop terus dijalankan sampai ketemu kluster
                                        flag = False

                                if flag == False:
                                    # jika katanya tidak berawalan 'per' diikuti dengan kata dasarnya
                                    # misalnya perkantoran, persaingan, pertarungan
                                    if not daftar_kata.startswith(daftar_prefiks[i]+kata_dasar) and not daftar_kata.startswith('per'+kata_dasar):
                                        # # hashing daftar katanya
                                        # hash_daftar_kata = rabin_karp_hash(daftar_kata)

                                        # # cek hasil hash kata berimbuhan dengan dataset kata benar
                                        # if str(hash_daftar_kata) in str(kata_benar_hash):
                                        #     # cek apakah belum ada kata berimbuhan yang benar di list hasil
                                        #     if daftar_kata not in hasil:
                                        #         # kalau belum ada masukin ke list hasil
                                        #         hasil.append(daftar_kata)
                                        # else:
                                        #     # cek apakah tidak ditemukan kluster, belum ada kata berimbuhannya di list hasil_salah, 
                                        #     # dan tidak berawalan memper
                                        #     if daftar_kata not in hasil_salah and daftar_kata != 'mempunyai':
                                        #         # masukkan kata ke dalam list hasil_salah
                                        #         hasil_salah.append(daftar_kata)

                                        # hashing daftar katanya

                                        # cek kata dengan dataset kata benar
                                        indeks_kata, kata = rabin_karp(daftar_kata, list_kata_benar)

                                        # jika ditemukan indeks kata    
                                        if indeks_kata:
                                            indeks_kata_benar = indeks_kata[0]
                                            # cek apakah kata sudah ada dalam variabel hasil
                                            if list_kata_benar[indeks_kata_benar] not in hasil:
                                                # jika belum ada, masukkan kata ke dalam variabel hasil
                                                hasil.append(list_kata_benar[indeks_kata_benar])
                                        # jika ditemukan katanya
                                        else:
                                            kata_salah = kata[0]
                                            # cek apakah kata sudah ada dalam variabel hasil salah
                                            if kata_salah not in hasil_salah:
                                                # jika belum ada, masukkan kata ke dalam variabel hasil salah
                                                hasil_salah.append(kata_salah)
    return hasil, hasil_salah

def solusi_kata_benar(kata_tidak_luluh, dataset_kata_benar):
    # if len(kata_luluh) == 0:
    #     print('Tidak ditemukan ejaan kata luluh yang benar')
    # else:
    #     for i in range(len(kata_luluh)):
    #         print('Kata ' + kata_luluh[i] + ' sudah sesuai dengan ejaan kamus besar bahasa Indonesia')

    solusi_terbaik = []
    # solusi_kurang_tepat = []
    solusi_tidak_ditemukan = []

    # print(kata_tidak_luluh)
    
    if len(kata_tidak_luluh) == 0:
        # print('Tidak ditemukan kesalahan eja kata luluh')
        return -1
    else:
        for j in range(len(kata_tidak_luluh)):
            # solusi_kata, skor_kemiripan_kata_salah = process.extractOne(kata_tidak_luluh[j], dataset_kata_benar)
            solusi = process.extract(kata_tidak_luluh[j], dataset_kata_benar)
            skor_kemiripan_tertinggi = 0
            solusi_kata = ''
            # print(solusi)

            for item in solusi:
                kata = item[0]
                skor = item[1]

                # buat variabel baru untuk menampung kata dasar dari solusi kata dan kata tidak luluhnya
                kata_dasar_solusi_kata = stemmer.stem(kata)
                kata_dasar_kata_tidak_luluh = stemmer.stem(kata_tidak_luluh[j])

                # cek apakah nilai dari variabel skor lebih besar dari nilai dari variabel skor_kemiripan_tertinggi
                # dan apakah kata dasar dari solusi kata dan kata dasar dari kata tidak luluhnya sama
                if skor > skor_kemiripan_tertinggi and kata_dasar_solusi_kata == kata_dasar_kata_tidak_luluh:
                    skor_kemiripan_tertinggi = skor
                    solusi_kata = kata

            # cek apakah skor_kemiripan_tertingginya lebih besar dari 88
            if skor_kemiripan_tertinggi > 88:
                # print('Solusi terbaik untuk kata ' + kata_tidak_luluh[j].upper() + ' adalah kata ' + solusi_kata.upper() + ' dengan persentase kemiripan sebesar ' + str(skor_kemiripan_kata_salah) + '%')

                # jika ya, masukkan kata_tidak_luluh[j], solusi_kata, dan skor_kemiripan_tertinggi ke dalam list solusi_terbaik
                solusi_terbaik.append((kata_tidak_luluh[j], solusi_kata, str(skor_kemiripan_tertinggi)))
                # return kata_tidak_luluh[j], solusi_kata, str(skor_kemiripan_kata_salah)
            # elif skor_kemiripan_tertinggi > 0 and skor_kemiripan_tertinggi <= 70:
            #     solusi_kurang_tepat.append((kata_tidak_luluh[j], solusi_kata, str(skor_kemiripan_tertinggi)))

            # jika skor_kemiripan_tertingginya kurang dari atau sama dengan 88
            else:
                # masukkan kata_tidak_luluh[j], solusi_kata, dan skor_kemiripan_tertinggi ke dalam list solusi_tidak_ditemukan
                solusi_tidak_ditemukan.append((kata_tidak_luluh[j], solusi_kata, str(skor_kemiripan_tertinggi)))
                # print('Solusi kata ' + kata_tidak_luluh[j] + ' tidak ditemukan')
                # data_list = (kata_tidak_luluh[j], solusi, str(skor_kemiripan_tertinggi))
                # cek apakah kata_tidak_luluh[j] pada data_list tidak ada pada list solusi_tidak_ditemukan
                # if not any(data_list[0] == item[0] for item in solusi_tidak_ditemukan):
                    # jika tidak ada, masukkan kata_tidak_luluh[j], solusi_kata, dan skor_kemiripan_tertinggi
                    # pada variabel solusi_tidak_ditemukan
                    # solusi_tidak_ditemukan.append(data_list)
                        # return kata_tidak_luluh[j]
                # # cek apakah nilai variabel skor lebih besar dari nilai variabel skor_kemiripan_tertinggi
                # # dan apakah kata dasar dari solusi kata tidak sama dengan kata dasar dari kata tidak luluhnya
                # elif skor > skor_kemiripan_tertinggi and kata_dasar_solusi_kata != kata_dasar_kata_tidak_luluh:
                #     data_list = (kata_tidak_luluh[j], solusi_kata, str(skor_kemiripan_tertinggi))
                #     # cek apakah kata_tidak_luluh[j] pada data_list tidak ada pada list solusi_tidak_ditemukan
                #     if not any(data_list[0] == item[0] for item in solusi_tidak_ditemukan):
                #         # jika tidak ada, masukkan kata_tidak_luluh[j], solusi_kata, dan skor_kemiripan_tertinggi
                #         # pada variabel solusi_tidak_ditemukan
                #         solusi_tidak_ditemukan.append(data_list)

        return solusi_terbaik, solusi_tidak_ditemukan

            # kata_dasar_solusi_kata = stemmer.stem(solusi_kata)
            # kata_dasar_kata_tidak_luluh = stemmer.stem(kata_tidak_luluh[j])
            # if skor_kemiripan_kata_salah > 88 and kata_dasar_solusi_kata == kata_dasar_kata_tidak_luluh:
            #     # print('Solusi terbaik untuk kata ' + kata_tidak_luluh[j].upper() + ' adalah kata ' + solusi_kata.upper() + ' dengan persentase kemiripan sebesar ' + str(skor_kemiripan_kata_salah) + '%')
            #     solusi_terbaik.append((kata_tidak_luluh[j], solusi_kata, str(skor_kemiripan_kata_salah)))
            #     # return kata_tidak_luluh[j], solusi_kata, str(skor_kemiripan_kata_salah)
            # elif skor_kemiripan_kata_salah > 0 and skor_kemiripan_kata_salah <= 88:
            #     # print('Solusi kata ' + kata_tidak_luluh[j] + ' tidak ditemukan')
            #     solusi_tidak_ditemukan.append(kata_tidak_luluh[j])
            #     # return kata_tidak_luluh[j]

        # return solusi_terbaik, solusi_tidak_ditemukan

def format_time(duration):
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    return f"{hours} hours, {minutes} minutes, {seconds} seconds"

factory = StemmerFactory()
stemmer = factory.create_stemmer()

@app.route('/', methods=['GET', 'POST'])
def index():
    global stemmer

    kata_dasar_file_path = 'D:\Skripsi\Website\dataset_kata_dasar.xlsx'
    kata_benar_file_path = 'D:\Skripsi\Website\dataset_kata_benar.xlsx'

    daftar_kata_dasar = pd.read_excel(kata_dasar_file_path)
    list_kata_dasar = daftar_kata_dasar['kata dasar'].values.tolist()

    daftar_kata_benar = pd.read_excel(kata_benar_file_path)
    list_kata_benar = daftar_kata_benar['kata benar'].values.tolist()

    if request.method == 'POST':
        start_time = time.time()
        print(start_time)
        plain_text = request.form['input_berita']
        if not plain_text:
            return render_template('index.html')
        else:
            preprocess_berita = preprocess(plain_text)
            hasil_kata_benar, hasil_kata_salah = deteksi_kata_luluh(preprocess_berita, list_kata_dasar, list_kata_benar)
            hasilnya = solusi_kata_benar(hasil_kata_salah, list_kata_benar)
            end_time = time.time()
            print(end_time)
            execution_time = end_time - start_time
            formatted_time = format_time(execution_time)
            print("Execution Time:", formatted_time)
            return render_template('hasil.html', hasil_kata_benar=hasil_kata_benar, hasil_kata_salah=hasilnya, berita=plain_text, list_kata_salah=hasil_kata_salah)
    return render_template('index.html')
    
# @app.route('/hasil', methods=['POST'])
# def hasil():
#     input_berita = request.form['input_berita']
#     return render_template('hasil.html', result=hasil)