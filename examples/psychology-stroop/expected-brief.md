# Scientific brief - psychology

Ontology v0.1.0 | 12 records | bibliographic verification only; full texts were not read.


## Observations (6)

- **PSY-001** [OBSERVED / PRESENT / MEASUREMENT] Ölçüm dosyasında uyumsuz (incongruent) koşulda 12 denemede tepki süreleri 798–971 ms aralığındadır; ortalama 897 ms.
  - scope: measurements.csv
  - claim limit: Yalnızca bu sentetik dosyadaki değerleri raporlar; gerçek katılımcı verisi değildir ve bireysel bir sonuç ileri sürmez.

- **PSY-002** [OBSERVED / PRESENT / MEASUREMENT] Aynı dosyada uyumlu (congruent) koşulda 12 denemede tepki süreleri 644–729 ms aralığındadır; ortalama 684 ms.
  - scope: measurements.csv
  - claim limit: Yalnızca bu sentetik dosyadaki değerleri raporlar; gerçek katılımcı verisi değildir.

- **PSY-003** [OBSERVED / PRESENT / MEASUREMENT] Uyumsuz koşulun tepki süreleri uyumlu koşulun tepki sürelerinden daha uzundur; iki setin aralıkları kesişmez.
  - scope: measurements.csv
  - claim limit: İki koşulun karşılaştırmasıdır; farkın nedenine dair bir iddia içermez ve sentetik veriye dayanır.

- **PSY-004** [CANDIDATE / NOT_REPRESENTED / MEASUREMENT] Bu veri setinde yaş, okuryazarlık düzeyi veya klinik tanı bilgisi kaydedilmemiştir.
  - scope: measurements.csv
  - claim limit: Yokluk yalnızca bu sentetik dosya için söylenmiştir; demografik veya bireysel bir iddia kurulamaz.

- **PSY-005** [DOCUMENTED_CLAIM / UNDER_IMPLEMENTED / SOURCE] Stroop (1935), renk-kelime uyumsuzluğunun renk adlandırma süresini uzattığını bildirmiştir.
  - scope: Stroop (1935) bibliographic record
  - claim limit: Kaynağın kendi bildirdiği bulgunun kaydıdır; bu paketin sentetik verisiyle doğrulanmış bir gözlem değildir.

- **PSY-012** [CANDIDATE / NOT_REPRESENTED / MEASUREMENT] Bu pakette otomatiklik ile kapasite hesaplarını ayıran bir manipülasyon uygulanmamıştır.
  - scope: measurements.csv
  - claim limit: Yokluk kaydıdır; mekanizma lehine veya aleyhine bir bulgu değildir.


## Canonical terms (2)

- **PSY-006** [INFERRED / PRESENT / EXTERNAL_SUBJECT] Uyumsuz koşulda etkisiz (neutral) tabana kıyasla gözlenen gecikme, Stroop interference etkisi olarak sınıflandırılabilir.
  - term: Stroop interference effect (TERM-STROOP-INTERFERENCE)
  - rivals: TERM-STROOP-FACILITATION
  - distinguishing test: Gecikme mi hızlanma mı gözleniyor? Etkisiz tabana göre yön belirlenmeden interference ile facilitation ayrılamaz.
  - scope: measurements.csv
  - claim limit: Grup düzeyinde bir etiketlemedir; tek bir katılımcı için interference sonucu değildir ve sentetik veriye dayanır.

- **PSY-007** [INFERRED / PRESENT / MEASUREMENT] Bağımlı değişken, tepki_onset ile yanıt arasındaki süre yani tepki süresidir (ms).
  - term: reaction time (RT) (TERM-REACTION-TIME)
  - rivals: TERM-RESPONSE-ACCURACY
  - distinguishing test: Bağımlı değişken hız mı doğruluk mu? Hız-doğruluk ödünleşmesinde ikisi ters yönde hareket edebilir, ayrı raporlanmalıdır.
  - scope: measurements.csv
  - claim limit: Bir performans ölçüsüdür; tek başına hangi sürecin neden olduğunu gösteremez.


## Theoretical frames (3)

- **PSY-008** [INFERRED / UNKNOWN / EXTERNAL_SUBJECT] Kelime okumanın otomatikliğinin renk adlandırmayla rekabet ettiği çerçeve, uyumsuz koşuldaki gecikmeyi yorumlamak için kullanılabilir.
  - theory: automaticity account of Stroop interference [VERIFIED_BIBLIOGRAPHIC] (THEORY-AUTOMATICITY-ACCOUNT)
      source: MacLeod, C. M. (1991), 'Half a century of research on the Stroop effect: An integrative review', Psychological Bulletin, 109(2), 163-203 | locator: https://doi.org/10.1037/0033-2909.109.2.163
  - what it explains here: Çerçeve bu kayıtta yalnızca grup düzeyindeki ortalama fark için bir yorumdur; otomatikliğin kendisi ölçülmemiştir.
  - scope: measurements.csv
  - claim limit: Yorum düzeyinde bir bağlantıdır; otomatiklik ölçülmediği için mekanizma kanıtı değildir.

- **PSY-009** [CANDIDATE / UNKNOWN / EXTERNAL_SUBJECT] Uyumsuz koşulda katılımcılar daha dikkatli yanıt vermeyi seçerek yavaşlamış olabilir.
  - theory: speed-accuracy tradeoff [UNVERIFIED] (THEORY-SPEED-ACCURACY-TRADEOFF)
      source: UNVERIFIED - a locator for the speed-accuracy tradeoff literature is still required | locator: (none)
  - what it explains here: Bu bir rakip yorumdur; bu veri setinde doğruluk tek yönlü olduğu için hız-ödünleşmesi ayrılamaz.
  - scope: measurements.csv
  - claim limit: Doğrulanmış kaynağı olmayan bir teoriye aday bağlantıdır; T6 gereği CANDIDATE düzeyini aşamaz.

- **PSY-010** [CANDIDATE / UNKNOWN / EXTERNAL_SUBJECT] Kısıtlı işlem kapasitesi de aynı gecikmeyi üretebilir; bu veri otomatiklik ile kapasite hesaplarını ayıramaz.
  - theory: limited-capacity / attentional account [VERIFIED_BIBLIOGRAPHIC] (THEORY-CAPACITY-ACCOUNT)
      source: MacLeod, C. M. (1991), 'Half a century of research on the Stroop effect: An integrative review', Psychological Bulletin, 109(2), 163-203 | locator: https://doi.org/10.1037/0033-2909.109.2.163
  - what it explains here: Rakip hesap bu kayıtta yalnızca alternatif olarak durur; ikisini ayıran bir manipülasyon yoktur.
  - scope: measurements.csv
  - claim limit: Rakip bir yorumdur; bu veriyle iki hesap arasında karar verilemez.


## Mechanism hypotheses (1)

- **PSY-011** [HYPOTHESIS / UNKNOWN / COUNTERFACTUAL] Kelime okuma sürecinin otomatikliği renk adlandırma tepkisiyle rekabet ederek tepki süresini artırır.
  - rivals: Kısıtlı işlem kapasitesi aynı gecikmeyi üretebilir (THEORY-CAPACITY-ACCOUNT); Yanıt dikkatliliğindeki değişiklik süreyi uzatmış olabilir (THEORY-SPEED-ACCURACY-TRADEOFF)
  - falsifier: Otomatiklik hesabına göre okuma otomatikliğini bozan bir manipülasyon (ör. bozuk yazı tipiyle sunulan kelimeler) uyumsuzluk gecikmesini belirgin biçimde azaltmalıdır; gecikme değişmiyorsa hesap bu veriyle desteklenmez.
  - scope: measurements.csv
  - claim limit: Bu bir mekanizma hipotezidir; bu pakette otomatiklik veya kapasite doğrudan ölçülmemiştir.

## Coverage: unknown / absent under scope (6)

Listed above with their claim limits: PSY-004 [NOT_REPRESENTED], PSY-008 [UNKNOWN], PSY-009 [UNKNOWN], PSY-010 [UNKNOWN], PSY-011 [UNKNOWN], PSY-012 [NOT_REPRESENTED].

A zero-finding section is a coverage statement, not success. Every link above is CANDIDATE/INFERRED/HYPOTHESIS unless its own evidence says otherwise.
