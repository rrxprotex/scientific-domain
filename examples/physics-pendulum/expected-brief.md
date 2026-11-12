# Scientific brief - physics

Ontology v0.1.0 | 14 records | bibliographic verification only; full texts were not read.


## Observations (7)

- **PHY-001** [OBSERVED / PRESENT / MEASUREMENT] Ölçüm dosyasında 0,20 m uzunluklu sarkaç için 20 tam salınımlık üç denemede hesaplanan periyot değerleri 0,895–0,902 s aralığındadır (T-01–T-03).
  - scope: measurements.csv
  - claim limit: Yalnızca bu sentetik dosyadaki değerleri raporlar; gerçek bir deneyden ölçülmemiştir ve genel bir periyot sonucu ileri sürmez.

- **PHY-002** [OBSERVED / PRESENT / MEASUREMENT] 0,50 m uzunluk için 20 tam salınımlık üç denemede hesaplanan periyot değerleri 1,413–1,426 s aralığındadır (T-07–T-09).
  - scope: measurements.csv
  - claim limit: Yalnızca bu sentetik dosyadaki değerleri raporlar; nedensel bir iddia içermez ve gerçek ölçüm değildir.

- **PHY-003** [OBSERVED / PRESENT / MEASUREMENT] 0,50 m sarkacın ölçülen periyot değerleri 0,20 m sarkacın değerlerinden daha büyüktür ve iki setin belirsizlik aralıkları kesişmez.
  - scope: measurements.csv
  - claim limit: İki uzunluk setinin karşılaştırmasıdır; farkın nedenine dair bir iddia içermez ve sentetik veriye dayanır.

- **PHY-004** [OBSERVED / PRESENT / MEASUREMENT] 0,50 m uzunlukta 0,05–0,20 kg kütlelerle yapılan üç denemede periyot değerleri 1,413–1,426 s aralığındadır.
  - scope: measurements.csv
  - claim limit: Kütle kontrollü bir değişken olarak sınanmamıştır; bu kayıttan periyodun kütleyle değişmediği sonucu çıkarılamaz.

- **PHY-005** [CANDIDATE / NOT_REPRESENTED / MEASUREMENT] Bu veri setinde 10,6°'den büyük başlangıç açısıyla yapılmış deneme yoktur.
  - scope: measurements.csv
  - claim limit: Yokluk yalnızca bu sentetik dosya için söylenmiştir; büyük açı davranışına dair bir bulgu değildir.

- **PHY-006** [CANDIDATE / NOT_REPRESENTED / MEASUREMENT] Hava direnci, pivot sürtünmesi ve ip esnemesi bu veri setinde ölçülmemiştir.
  - scope: measurements.csv
  - claim limit: Ölçülmeyen nicelikler hakkında açıklama yapılamaz; bu kayıt yalnızca kapsamı belirler.

- **PHY-007** [CANDIDATE / UNKNOWN / MEASUREMENT] Bu pakette g'nin bağımsız referans ölçümü bulunmaz; g değeri yalnızca model yoluyla türetilir.
  - scope: measurements.csv
  - claim limit: Modelle türetilen bir g değeri bağımsız ölçüm değildir; bu kayıt o sınırı korur.


## Canonical terms (3)

- **PHY-008** [INFERRED / PRESENT / MEASUREMENT] Deney düzeneği, kütlesi ihmal edilebilir ipe asılı küçük küreli basit sarkaç modeli olarak sınıflandırılabilir.
  - term: simple pendulum (TERM-SIMPLE-PENDULUM)
  - rivals: TERM-PHYSICAL-PENDULUM
  - distinguishing test: Küre çapı ip uzunluğuna göre küçük ve ip kütlesi küre kütlesine göre ihmal edilebilir düzeyde; kütle dağılımı ve atalet momenti önemli olsaydı fiziksel sarkaç tercih edilirdi.
  - scope: measurements.csv
  - claim limit: Bir model sistem etiketidir; düzenek idealdir demek değildir, pivot sürtünmesi ölçülmemiştir.

- **PHY-009** [INFERRED / PRESENT / MEASUREMENT] Ölçülen büyüklük saniye/salınım cinsinden periyottur; her denemede değer elapsed_time_s / cycle_count ile hesaplanmıştır.
  - term: period of oscillation (T) (TERM-PERIOD)
  - rivals: TERM-FREQUENCY
  - distinguishing test: Birim saniye/salınım yani periyot; cycles/s yani frekans olsaydı ters çevrilmesi gerekirdi. İki nicelik birbirine karıştırılmamalı.
  - scope: measurements.csv
  - claim limit: Bir nicelik etiketidir; periyot değerinin neyin yönetiminde olduğuna dair bir iddia içermez.

- **PHY-010** [INFERRED / PRESENT / MEASUREMENT] Tüm denemeler 5,0°–10,6° başlangıç açısı aralığında yapılmıştır; küçük açı yaklaşımının geçerlilik sınırı olan yaklaşık 15° içindedir.
  - term: small-angle approximation (TERM-SMALL-ANGLE-APPROXIMATION)
  - rivals: TERM-ANHARMONIC-CORRECTION
  - distinguishing test: Açılar 15° sınırının altında; büyük açı düzeltmesi gerekseydi periyodun genlikle büyümesi beklenirdi, bu veride genlik etkisi aranmadı.
  - scope: measurements.csv
  - claim limit: Yaklaşımın sınırı yalnızca bu açı aralığı için geçerlidir; büyük açı davranışı hakkında sonuç vermez.


## Theoretical frames (3)

- **PHY-011** [INFERRED / UNDER_IMPLEMENTED / MEASUREMENT] Ölçülen periyot–uzunluk ilişkisi, basit sarkaç modelinin T = 2*pi*sqrt(L/g) öngörüsüyle karşılaştırılabilir.
  - theory: simple pendulum model (small-angle) [VERIFIED_BIBLIOGRAPHIC] (THEORY-SIMPLE-PENDULUM-MODEL)
      source: OpenStax, University Physics Volume 1, section 15.4 'Pendulums' (small-angle solution and period formula) | locator: https://openstax.org/books/university-physics-volume-1/pages/15-4-pendulums
  - what it explains here: Model bu kayıtta yalnızca L = 0,20–0,80 m ve açı ≤ 10,6° aralığında değerlendirilir; örtüşme belirsizlik aralığı içindedir.
  - scope: measurements.csv
  - claim limit: Model, varsayımları içinde geçerli bir ilişkidir; sentetik veriye oturması modelin doğrulanması anlamına gelmez.

- **PHY-012** [CANDIDATE / UNKNOWN / MEASUREMENT] Periyot değerleri ±0,010 s beyan edilen belirsizlik aralığıyla birlikte raporlanmalıdır.
  - theory: measurement error analysis [UNVERIFIED] (THEORY-ERROR-ANALYSIS)
      source: UNVERIFIED - a metrology reference locator (e.g. the GUM) is still required | locator: (none)
  - what it explains here: Bu kayıtta kural yalnızca raporlama disiplini olarak uygulanır; kaynağı doğrulanmış bir yöntem metni bu pakette yoktur.
  - scope: measurements.csv
  - claim limit: Doğrulanmış kaynak yoktur; bu bağlantı aday düzeyindedir ve yöntemsel bir onay sayılmaz.

- **PHY-013** [CANDIDATE / UNKNOWN / MEASUREMENT] Salınım genliğinin zamanla azalması, sürtünme kaybıyla yorumlanabilir; bu pakette bu yorum test edilmemiştir.
  - theory: damped harmonic oscillation [VERIFIED_BIBLIOGRAPHIC] (THEORY-DAMPED-OSCILLATION)
      source: 'Tracking the Acceleration Due to Gravity and Damping of a Pendulum: A Video Analysis', Physics Education Research Journal 5(2), 2023 | locator: https://doi.org/10.21580/perj.2023.5.2.16614
  - what it explains here: Yorum adaydır: bu veri setinde genliğin zaman serisi kaydedilmemiştir.
  - scope: measurements.csv
  - claim limit: Rakip bir çerçevedir; sürtünme ölçülmediği için bu kayıt bir kayıp kanıtı da değildir.


## Mechanism hypotheses (1)

- **PHY-014** [HYPOTHESIS / UNKNOWN / COUNTERFACTUAL] Yerçekimi kuvvetinin teğetsel bileşeni geri çağırıcı kuvvete neden olur ve bu kuvvet küçük açı rejiminde basit harmonik hareketi üretir.
  - rivals: Sürtünme ve hava direnci gözlenen sapmaları açıklıyor olabilir (THEORY-DAMPED-OSCILLATION); Zaman ölçümündeki sistematik hata farkları açıklıyor olabilir (TERM-SYSTEMATIC-ERROR)
  - falsifier: Geri çağırıcı kuvvet hesabı doğruysa bağımsız bir kuvvet ölçümü mg*sin(theta) değerini belirsizlik aralığı içinde vermelidir; kuvvet ölçümleri bu değeri karşılamazsa mekanizma bu düzenekte reddedilir.
  - scope: measurements.csv
  - claim limit: Bu bir mekanizma hipotezidir; bu pakette kuvvet ölçülmemiştir ve mekanizma doğrudan test edilmemiştir.

## Coverage: unknown / absent under scope (6)

Listed above with their claim limits: PHY-005 [NOT_REPRESENTED], PHY-006 [NOT_REPRESENTED], PHY-007 [UNKNOWN], PHY-012 [UNKNOWN], PHY-013 [UNKNOWN], PHY-014 [UNKNOWN].

A zero-finding section is a coverage statement, not success. Every link above is CANDIDATE/INFERRED/HYPOTHESIS unless its own evidence says otherwise.
