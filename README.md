# ALMS Video İndirme Aracı

Advancity LMS sistemi kullanan sitelerden ders videolarını indirmenizi sağlar.

## Gereksinimler

- Python 3.6.5 veya üstü
- pycurl

## Kurulum

### Python kullanarak

1. ```bash
    pip install -r requirements.txt
    ```
2. ```bash
    python app.py
    ```

### Windows uygulamasını kullanarak

1. Releases sayfasından en son sürümü indirdikten sonra çalıştırın.
Herhangi bir kod ya da kütüphane indirmeye gerek yoktur.

## Kullanım

1. Açılan ekranda uzaktan eğitim sitesinin adresini herhangi bir ek olmadan (https:// gibi ekler olmadan) girin.
2. Ardından kopyaladığınız çerez değerini yapıştırın.
3. Ders listesinden ders seçimi yaptıktan sonra, video kayıtlarını indirebilirsiniz.

### Çerezleri Kopyalama

1. Uzaktan eğitim hesabınıza giriş yaptıktan sonra sağ tıklayıp öğeyi denetleye (inspect) veya F12 tuşuna basınız.
2. Açılan pencerede *Network* sekmesini açınız.
3. *Doc* filtresini seçtikten sonra sayfayı yenileyiniz.
4. Alttaki listede en üstte bulunan öğeyi seçtikten sonra *Request Headers* bölümünde *Cookie* yazısına sağ tıklayıp
   *Copy value* seçeneğini seçiniz.
![Çerezleri kopyalama](/docs/cookies.png "Çerezleri kopyalama")
