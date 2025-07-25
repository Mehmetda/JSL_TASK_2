# Medical RAG QA Chatbot (Dockerized)

## İçindekiler
- [Açıklama](#açıklama)
- [Kurulum ve Çalıştırma](#kurulum-ve-çalıştırma)
  - [Gereksinimler](#gereksinimler)
  - [Kurulum Adımları](#kurulum-adımları)
  - [Uygulamayı Başlatma](#uygulamayı-başlatma)
- [Kullanım](#kullanım)
- [Özellikler](#özellikler)
- [Notlar](#notlar)
- [Qdrant Arayüzü](#qdrant-arayüzü)
- [Geliştirme](#geliştirme)

## Açıklama
Kendi PDF veya DOCX dosyalarınızı yükleyip, bu dokümanlardan tıbbi sorulara yanıt alabileceğiniz bir Retrieval-Augmented Generation (RAG) tabanlı chatbot uygulamasıdır. Uygulama, yüklediğiniz dokümanları vektörlere ayırır ve Qdrant vektör veritabanında saklar. Böylece, sorduğunuz sorulara en alakalı doküman parçalarından yanıtlar üretir.

## Kurulum ve Çalıştırma

### Gereksinimler
- [Docker](https://www.docker.com/) ve [Docker Compose](https://docs.docker.com/compose/) kurulu olmalı.
- HuggingFace hesabınızdan bir erişim token'ı alınmalı.
- Bilgisayarınızda 4GB+ RAM önerilir (büyük modeller için daha fazlası gerekebilir).

### Docker ve Docker Compose Kurulumu
- **Windows/Mac:**
  - [Docker Desktop](https://www.docker.com/products/docker-desktop/) indirip kurun. Docker Compose bu paketle birlikte gelir.
- **Linux:**
  - Terminalde aşağıdaki komutları çalıştırarak Docker ve Compose'u kurabilirsiniz:
    ```sh
    sudo apt-get update
    sudo apt-get install docker.io docker-compose -y
    sudo systemctl start docker
    sudo systemctl enable docker
    ```
  - Kullanıcıyı docker grubuna ekleyin (isteğe bağlı):
    ```sh
    sudo usermod -aG docker $USER
    ```

### HuggingFace Token Alma
1. [HuggingFace](https://huggingface.co/) sitesine üye olun veya giriş yapın.
2. Sağ üstteki profil menüsünden "Settings" > "Access Tokens" bölümüne gidin.
3. "New token" diyerek bir token oluşturun ve kopyalayın.

### .env Dosyası Oluşturma
1. Proje kök dizininde `.env` adında bir dosya oluşturun.
2. İçine aşağıdaki satırı ekleyin (kendi tokenınızı kullanın):
   ```
   HF_TOKEN=senin_huggingface_tokenin
   ```

### Port Ayarları
- Varsayılan olarak uygulama 8000 portunda, Qdrant ise 6333 portunda çalışır.
- Eğer bu portlar başka bir uygulama tarafından kullanılıyorsa, `docker-compose.yml` dosyasındaki portları değiştirebilirsiniz.

### Kurulum Adımları
1. Proje dosyalarını bilgisayarınıza indirin veya klonlayın:
   ```sh
   git clone https://github.com/kullanici/Medical-RAG-using-Meditron-7B-LLM.git
   cd Medical-RAG-using-Meditron-7B-LLM
   ```
2. `.env` dosyasını oluşturduğunuzdan ve HuggingFace tokenınızı eklediğinizden emin olun.
3. Gerekli dosyaların (`requirements.txt`, `docker-compose.yml`, `Dockerfile`) mevcut olduğundan emin olun.

### Uygulamayı Başlatma
1. Terminalde proje dizinine gidin:
   ```sh
   cd Medical-RAG-using-Meditron-7B-LLM
   ```
2. Aşağıdaki komutla uygulamayı başlatın:
   ```sh
   docker-compose up --build
   ```
   - Bu komut, gerekli Docker imajlarını oluşturur ve konteynerleri başlatır.
   - İlk başlatmada model ve bazı dosyalar indirileceği için biraz zaman alabilir.
3. Başarıyla başlatıldığında, uygulama arayüzüne tarayıcınızdan [http://localhost:8000](http://localhost:8000) adresinden erişebilirsiniz.
4. Qdrant arayüzüne ise [http://localhost:6333/dashboard](http://localhost:6333/dashboard) adresinden ulaşabilirsiniz.

### Hata Durumunda Yapılacaklar
- Eğer uygulama başlamazsa veya hata alırsanız:
  - Logları görmek için:
    ```sh
    docker-compose logs -f
    ```
  - Port çakışması varsa, `docker-compose.yml` dosyasındaki portları değiştirin.
  - `.env` dosyanızın ve HuggingFace tokenınızın doğru olduğundan emin olun.
  - Gerekirse konteynerleri ve imajları temizleyip tekrar deneyin:
    ```sh
    docker-compose down
    docker-compose build --no-cache
    docker-compose up
    ```
- Sorun devam ederse, hata mesajını geliştiriciye iletebilirsiniz.

## Kullanım
- Web arayüzü üzerinden PDF veya DOCX dosyalarınızı yükleyin.
- Soru-cevap kutusuna tıbbi sorularınızı yazın.
- Sistem, yüklediğiniz dokümanlardan en alakalı yanıtı üretir ve ekranda gösterir.

## Özellikler
- **Çoklu Dosya Desteği:** PDF ve DOCX formatında birden fazla dosya yükleyebilirsiniz.
- **Gelişmiş Soru-Cevap:** Yüklediğiniz dokümanlardan tıbbi sorulara yanıt alabilirsiniz.
- **Vektör Arama:** Qdrant vektör veritabanı ile hızlı ve isabetli arama.
- **Kullanıcı Dostu Arayüz:** Basit ve anlaşılır web arayüzü.

## Notlar
- Yüklediğiniz her dosya otomatik olarak embedding'lere ayrılır ve vektör veritabanına eklenir.
- Sorduğunuz sorular, yüklediğiniz tüm dokümanlardan cevaplanır.
- Uygulama ilk başlatıldığında model ve bazı dosyalar indirilebilir, bu nedenle ilk açılış biraz uzun sürebilir.
- `.env` dosyanızda HuggingFace token'ınızın doğru olduğundan emin olun.

## Qdrant Arayüzü
- Qdrant vektör veritabanının yönetim paneline [http://localhost:6333/dashboard](http://localhost:6333/dashboard) adresinden erişebilirsiniz.
- Buradan koleksiyonları ve vektörleri görüntüleyebilirsiniz.

## Geliştirme
- Kodda veya arayüzde değişiklik yaptıktan sonra konteyneri yeniden başlatmanız gerekebilir:
  ```
  docker-compose restart
  ```
- Yeni bağımlılıklar eklediyseniz, imajı yeniden oluşturun:
  ```
  docker-compose up --build
  ```
- Geliştirme sırasında logları takip etmek için:
  ```
  docker-compose logs -f
  ```
- Sorun yaşarsanız, hata mesajlarını ve logları kontrol edin.
