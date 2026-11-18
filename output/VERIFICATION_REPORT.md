# NE India ethnomedicine meta-analysis: data verification and source gaps

Generated 2026-11-17 by `analysis/06_verify_against_papers.py`. The detail is in `output/verification_report.xlsx`, which has these sheets: Summary, Records, Records_to_check and Candidate_omissions.

## 1. Sources in the plan

There are 33 sources in total: NE5 has 26 and Assam V6 has 18, with 11 shared between them.

- **Included (30):** the papers are in `sources/pdf/`. S01 and S02 are full-text XML from Europe PMC. S10 is a scanned book chapter that was OCR'd, as were the table pages of S21 (pp. 4–9).
- **Excluded (3), because no PDF could be obtained:** S13 Basumatary et al. 2014 (Bodo-Kachari), S20 Nath et al. 2011 (Dimasa) and S32 Roy & Nath 2019 (Dimasa review). This removes 70 NE5 records and 85 V6 records.
- **Extra PDFs not in either dataset:** `sources/extra/X01` is Laskar & Das, a book chapter on the Dimasa of Dima Hasao that could replace S20/S32 for the Dimasa. `X02` is Begum et al. 2024 (*ERA* 27:43), a review of 12 papers on Dima Hasao and Karbi Anglong, which is useful for finding more sources and for comparison.

## 2. Record check results (records with a PDF)

| | NE5 | V6 |
|---|---|---|
| Species, part and use all found in the paper | 877 | 388 |
| Species found, part or use not near it in the text (often only a table-layout issue) | 162 | 191 |
| Name differs from the paper (synonym or spelling) | 19 | 17 |
| **Species not in the paper at all** | **86** | **68** |
| Excluded (no PDF) | 70 | 85 |

### Errors that need fixing

1. **S08, Baishya & Bora 2007 (Dibru-Saikhowa).**
   - The paper covers only **Mishing, Moran, Assamese and Bengali**, yet all 53 records are labelled "Khamti". The tribe needs to be re-assigned for each plant, using the community abbreviations the paper gives (Asm, Mor, ...).
   - **24 of the 53 species are not in this paper at all**, for example *Acorus calamus*, *Curcuma longa*, *Butea monosperma*, *Areca catechu* and *Oryza sativa*. They came from some other source.
   - In the other direction, the paper lists 121 species and about 68 binomials in it are not in the data.
2. **S16, Adhikary & Barman 2014 (Rabha).** The 18 "Moran" records (NE5 rows 462–479) cite this Rabha paper, but **15 of them are not in it**. The real Moran source is missing. Candidates: Borah, *Moran reproductive health* (Neliti PDF), and Kalita & Phukan, *Folk medicines used by the Moran, Tinsukia*.
3. **S03 Konyak and S04 Angami** are both labelled "Naga". They should be "Konyak Naga" and "Angami Naga".
4. **S17 (Tripura)** is labelled "Kokborok", which is a language. It should be "Tripuri" or "Reang", per record.
5. **S15 Jaiswal 2010** is a review, a secondary source. Either keep it with a flag or drop it to avoid counting the same plants twice.
6. **S07 Deori** has 7 species, and **S03 Konyak** has 7, that aren't in their papers. Each row is listed in Records_to_check, with the other papers that do contain that species in the `found_in_other_sources` column.
7. **Old names that may hide synonyms:** for example *Emblica officinalis* = *Phyllanthus emblica*, *Spilanthes paniculata* = *Acmella paniculata*, and *Curcuma domestica* = *C. longa*. Check these against the paper before deleting anything.

### Likely gaps in what was extracted (plants in the paper that are missing from the data)

These are candidates only and need manual review: some will be non-medicinal plants or names cited from other works.

| Source | Paper reports | Records in data | Candidate omissions |
|---|---|---|---|
| S14 Kutum 2011 (Mishing) | 86 species | 43 | 40 |
| S08 Baishya 2007 | 121 species | 53 | 68 |
| S19 Moyong (Mishmi) | 72 species | 29 | 43 |
| S26 Rinyo 2018 (Tagin) | 70 species (all uses) | 8 | 58 |
| S21 Ratan 2016 (Galo) | 37 medicinal | 27 | 13 |
| S33 Khan 2014 (Hmar/Manipuri/Barman) | 52 species | 11 (Barman only) | 38 |
| S02 Laldingliani 2022 (Mizo) | 93 species | 93 | 16 (mostly genus mentions in the discussion) |

## 3. Is the meta-analysis complete? No.

| State | Sources now | Tribes now | Main gaps |
|---|---|---|---|
| Arunachal | 8 | 8 | Monpa, Sherdukpen, Nocte, Wancho, Tangsa, Singpho, Idu Mishmi, Bugun, Miji |
| Assam (V6 + NE5) | 17 | 12 | Moran (missing source), Ahom, Hajong, Tai Phake, Barak Valley communities |
| Nagaland | 2 | 2 | Ao, Sumi, Lotha, Chakhesang, Rengma, Zeliang, Chang |
| Meghalaya | 2 (1 is a review) | 2 | **Garo** (no Meghalaya Garo source), War-Jaintia, Khasi (more studies) |
| Manipur | 1 (book chapter) | 1 | Tangkhul, Maring, Kabui/Rongmei, Kuki, Mao |
| Mizoram | 1 | 1 | Lai, Mara, Bru, Hmar |
| Tripura | 1 | 1 | Reang, Chakma, Halam, Jamatia, Bishnupriya Manipuri |

### Candidate sources to add (screen these against your inclusion criteria)

**Manipur**
- Tangkhul Naga, cultural consensus study, *ERA*: https://www.ethnobotanyjournal.org/index.php/era/article/view/7520
- Meitei sacred-grove trees, *IJTK* 2025: https://or.niscpr.res.in/index.php/IJTK/article/download/22353/4954/104863

**Tripura**
- Bishnupriya Manipuri people of Tripura, *ERA*: https://ethnobotanyjournal.org/index.php/era/article/view/7012
- Shil & Dutta Choudhury 2009, Reang of Dhalai: https://core.ac.uk/download/60543543.pdf
- Majumdar & Datta 2007, Tripuri, *NPR* 6(1): 66–73: https://nopr.niscpr.res.in/bitstream/123456789/7835/1/NPR%206(1)%2066-73.pdf
- Traditional knowledge of medicinal plants in tribes of Tripura, *AJTCAM*: https://journals.athmsi.org/index.php/ajtcam/article/view/4734

**Mizoram**
- Ralte & Singh 2024, Lai, Mara, Bru and others, *PLoS ONE*: https://doi.org/10.1371/journal.pone.0302792
- Western Mizoram 2024, *JEE*: https://link.springer.com/10.1186/s13002-023-00642-z

**Meghalaya, Garo**
- Marak & Lalnundanga 2019, Rongram Block: https://www.sciencevision.org/storage/journal-articles/January2019/Tu2KIEIaE1yTFs9qtWN3.pdf
- Garo bone-fracture healers, *Plant Archives* 2020: https://www.plantarchives.org/20-1/754-758%20(5596).pdf

**Nagaland**
- Ao tribe, Dimapur, *Vegetos*: https://vegetosindia.org/article/uncovering-ethnobotanical-wealth-and-traditional-medicinal-knowledge-of-the-ao-tribe-in-dimapur-district-of-nagaland-india
- Chakhesang / Ao anti-diabetic plants, *Plant Science Today*: https://horizonepublishing.com/journals/index.php/PST/article/download/2602/2733/19574

**Arunachal**
- Monpa, Zemithang, PMC: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5371772/
- Review of 14 Arunachal tribes, *ERA* (use it to find the primary studies): https://www.ethnobotanyjournal.org/index.php/era/article/view/3005

**Assam, Moran (to replace the missing source)**
- Borah, Moran reproductive health: https://media.neliti.com/media/publications/263243-various-ethno-medicinal-plants-used-for-0a069108.pdf
- Kalita & Phukan, Moran folk medicine: https://krishi.icar.gov.in/ohs-2.3.1/index.php/record/view/216878
- Buragohain 2011, Tinsukia communities: https://updatepublishing.com/journal/index.php/rrst/article/view/781

**Reviews to cite and to mine for further sources (not as data)**
- Jha & Smith-Hall 2023, 255 NE India publications, *ERA*: https://www.ethnobotanyjournal.org/index.php/era/article/view/4723
- Barbhuiya et al. 2022, Barak Valley systematic review: https://koreascience.kr/article/JAKO202227152324591.page

### What a reviewer will expect

- **A written search strategy and PRISMA flow diagram:** the databases searched, search strings, dates, inclusion and exclusion criteria, and the reason each paper was excluded. Record the three PDFs you couldn't obtain as "not retrieved".
- **A rule for including studies**, for example: primary field survey, medicinal use, species identified to binomial, and tribe and district stated. Reviews such as S15, S32 and X02 should be excluded as data under this rule.
- **Inclusion based on the search, not on how many papers each state has.** Coverage should come from the search; per-state counts should be reported as a limitation, not filled in by hand-picking papers.

## 4. Sources added (v2, 2026-11-17)

These were extracted by `analysis/08_extract_new.py` and merged by `analysis/09_merge_v2.py`, giving `output/NE_combined_v2.xlsx`. Each paper's species count was checked against the number it reports.

| ID | Paper | State | Tribe | Records | Species (paper says) |
|---|---|---|---|---|---|
| N03 | Majumdar & Datta 2007, *NPR* 6(1) | Tripura | Tripuri | 50 | 50 (50) |
| N05 | Marak & Mathew 2020, *Plant Archives* 20(1) | Meghalaya | Garo | 14 | 14 (bone fracture only) |
| N06 | Ralte et al. 2024, *PLoS ONE* | Mizoram | Mizo, Chakma, Bru, Lai, Mara, Hmar, Bawm | 103 | 102 (102) |
| N07 | Western Mizoram 2024, *JEE* | Mizoram | Mizo | 124 | 124 (124) |
| N08 | Monpa, Zemithang (PMC5371772) | Arunachal | Monpa | 51 | 51 (53 listed, 51 used in the 24 medicines) |
| N09 | Shimrah et al., Tangkhul Naga, *ERA* | Manipur | Tangkhul Naga | 37 | 37 (37) |
| N10 | Dhar et al. 2025, *ERA* 31:59 | Tripura | Bishnupriya Manipuri (non-ST, flagged) | 82 | 82 (82) |

For these new records, `ActedUpon` (body system) was assigned automatically from the disease text, and each one is flagged so it can be reviewed.

Not added yet:
- **N01 Moran (Borah), N02 Reang (Shil), N04 Garo (Marak & Lalnundanga 2019), N11 Tripura (AJTCAM):** the PDFs need to be downloaded by hand.
- **N12 Ao Naga diabetes:** the plant list is only in the supplementary file.

**v2 totals:** 1,822 records, 37 sources, 925 species, 539 genera, 151 families, 43 tribes. After applying APG IV family rules by genus, no species is listed under more than one family.
