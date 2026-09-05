_Created: 10-06-2026 · Last updated: 05-09-2026_

# Whitney ↔ DCS editorial worklist

_Source: `dcs_full.sqlite` (2026 CoNLL-U); generated 2026-06-10._

Actionable discrepancies for correcting `src/app_data.json`. The `id` is the lexicon entry id. **This is a review aid, not an oracle** — DCS's grammar field is itself lexicon metadata and the corpus signal is a coarse heuristic; confirm before editing.

## A. Class conflicts the corpus backs AGAINST Whitney (4)

Highest-priority: Whitney's class set is disjoint from DCS **and** the corpus present-stem signal points to the DCS class. Consider adding/adjusting the class.

| id | root | Whitney | DCS | corpus signal | tokens |
|---|---|---|---|---|---|
| 571 | 1 mṛ | 1 | 4,9 | IV | 2615 |
| 572 | 2 mṛ | 1 | 4,9 | IV | 2615 |
| 705 | vadh | 1 | 4 | IV | 1236 |
| 234 | cūṣ | 4 | 1 | I/VI | 22 |

## B. Other class conflicts — review (99)

Disjoint class sets where the corpus signal does not corroborate DCS (sometimes it backs Whitney, meaning DCS's grammar field is the outlier — do not 'correct' these).

| id | root | Whitney | DCS | corpus signal | tokens |
|---|---|---|---|---|---|
| 170 | gam | 1,2 | 6 | I/VI | 18341 |
| 815 | śru | 2,5 | 4 | VIII | 10505 |
| 608 | yuj | 2,6,7 | 1 | II/III (athematic) | 5933 |
| 269 | jñā | 1,9 | 4 | IX | 5041 |
| 546 | man | 3,4,8 | 1 | IV | 4697 |
| 258 | 1 ji | 1,2 | 9 | X/caus-denom | 4082 |
| 259 | 2 ji | 1,2 | 9 | X/caus-denom | 4082 |
| 477 | prach | 6 | 1 | I/VI | 2851 |
| 909 | har | 4 | 2,9 | I/VI | 2792 |
| 854 | sṛj | 1,6 | 2 | I/VI | 2749 |
| 494 | bandh | 1,9 | 4 | IX | 2654 |
| 324 | tyaj | 1 | 3 | I/VI | 2417 |
| 792 | śudh | 1,2,4 | 7 | IV | 2410 |
| 26 | āp | 5 | 1 | V | 2314 |
| 242 | chid | 7 | 1 | II/III (athematic) | 2139 |
| 521 | bhid | 7 | 3 | II/III (athematic) | 2047 |
| 767 | śak | 5 | 4 | V | 1952 |
| 20 | 1 aś | 5,9 | 1 | V | 1948 |
| 21 | 2 aś | 5,9 | 1 | V | 1948 |
| 613 | rakṣ | 1 | 4 | I/VI | 1929 |
| 724 | vāh | 1 | 2 | I/VI | 1845 |
| 766 | śaṃs | 1 | 2 | I/VI | 1785 |
| 250 | jap | 1 | 4 | I/VI | 1702 |
| 745 | vṛdh | 1 | 6 | I/VI | 1619 |
| 629 | ram | 1,9 | 4 | I/VI | 1553 |
| 388 | dviṣ | 2,6 | 1 | I/VI | 1343 |
| 856 | sev | 1 | 4 | VIII | 1328 |
| 402 | dhṛ | 1 | 4 | I/VI | 1229 |
| 141 | 1 kṣi | 1,2,6 | 4 | II/III (athematic) | 1181 |
| 142 | 2 kṣi | 1,2,6 | 4 | II/III (athematic) | 1181 |
| 405 | dhyā | 2,4 | 3 | IV | 1164 |
| 600 | yam | 1,2 | 6 | I/VI | 1093 |
| 384 | dru | 1 | 9 | I/VI | 1073 |
| 456 | piṣ | 6,7 | 1 | I/VI | 1062 |
| 734 | viś | 6 | 3 | I/VI | 1053 |
| 830 | sad | 1,2 | 6 | I/VI | 953 |
| 846 | su | 3,5 | 6 | V | 878 |
| 369 | duh | 2,4,6 | 1 | I/VI | 806 |
| 682 | lip | 6 | 4 | I/VI | 778 |
| 165 | khyā | 2 | 4 | II/III (athematic) | 777 |
| 790 | śuc | 1,2,4 | 6 | I/VI | 777 |
| 506 | bhañj | 7 | 4 | II/III (athematic) | 754 |
| 841 | sic | 1,6 | 4 | I/VI | 687 |
| 813 | 1 śrī | 9 | 4 | II/III (athematic) | 644 |
| 814 | 2 śrī | 9 | 4 | II/III (athematic) | 644 |
| 779 | śā | 3,6 | 4 | II/III (athematic) | 519 |
| 45 | īkṣ | 1 | 4 | I/VI | 473 |
| 187 | guh | 1 | 6 | I/VI | 468 |
| 120 | krī | 9 | 1 | II/III (athematic) | 439 |
| 464 | puṣ | 1,4,9 | 6 | IV | 438 |
| 684 | lih | 2,6 | 4 | I/VI | 405 |
| 75 | ṛdh | 4,5,7 | 6 | V | 392 |
| 156 | khad | 6 | 1 | I/VI | 369 |
| 157 | khan | 1 | 2 | I/VI | 352 |
| 431 | nud | 6 | 7 | I/VI | 332 |
| 576 | mṛj | 1,2,6,7 | 3 | I/VI | 298 |
| 227 | cit | 1 | 3 | I/VI | 266 |
| 124 | kruś | 1 | 4 | I/VI | 238 |
| 138 | kṣar | 1 | 2 | I/VI | 220 |
| 90 | kāṅkṣ | 1 | 2 | I/VI | 202 |
| 55 | 1 ukṣ | 6 | 4 | I/VI | 191 |
| 56 | 2 ukṣ | 6 | 4 | I/VI | 191 |
| 794 | 1 śuṣ | 4 | 6 | IV | 166 |
| 795 | 2 śuṣ | 4 | 6 | IV | 166 |
| 476 | pyā | 4 | 2 | II/III (athematic) | 165 |
| 504 | bhakṣ | 1 | 4 | I/VI | 162 |
| 209 | ghṛṣ | 1 | 4 | I/VI | 156 |
| 222 | carv | 4 | 1 | — | 151 |
| 582 | mṛṣ | 1,4 | 2 | IV | 150 |
| 443 | pad | 2,4 | 1 | IV | 134 |
| 896 | sraṃs | 1 | 9 | I/VI | 133 |
| 670 | lajj | 6 | 1 | I/VI | 109 |
| 342 | dabh | 1,5 | 4 | II/III (athematic) | 96 |
| 820 | śliṣ | 1,4 | 6 | IV | 92 |
| 365 | du | 5 | 4 | V | 82 |
| 694 | lū | 5,9 | 8 | V | 81 |
| 385 | druh | 4 | 6 | IV | 70 |
| 83 | kan | 4 | 1 | — | 56 |
| 401 | dhūrv | 1 | 6 | I/VI | 50 |
| 581 | mṛś | 6 | 2 | I/VI | 33 |
| 918 | hīḍ | 1 | 6 | — | 29 |
| 580 | mṛdh | 1,6 | 9 | I/VI | 22 |
| 486 | pluṣ | 1 | 4 | — | 21 |
| 858 | skambh | 1,5,9 | 8 | IX | 20 |
| 31 | iṅg | 1 | 4 | I/VI | 15 |
| 112 | kṛś | 4 | 1 | IV | 8 |
| 725 | 1 vic | 3,7 | 4 | I/VI | 8 |
| 726 | 2 vic | 3,7 | 4 | I/VI | 8 |
| 660 | rup | 4 | 6 | — | 6 |
| 2 | 1 akṣ | 1 | 5 | ? | 4 |
| 3 | 2 akṣ | 1 | 5 | ? | 4 |
| 736 | viṣṭ | 1 | 6 | — | 2 |
| 778 | śas | 1,2 | 4 | II/III (athematic) | 2 |
| 917 | hiṇḍ | 1 | 4 | — | 2 |
| 536 | bhrī | 9 | 7 | I/VI | 1 |
| 574 | mṛc | 4 | 6 | — | 1 |
| 859 | sku | 2,5,9 | 8 | — | 1 |
| 9 | aṇṭh | 6 | 1 | — | 0 |
| 563 | mīv | 1 | 6 | — | 0 |

## C. Whitney PPP stems unattested in the corpus (208)

PPP forms Whitney lists that never appear in DCS. High-frequency roots first (a missing PPP on a common root is more suspect; rare/Vedic roots may simply be unattested).

| id | root | unattested PPP | tokens |
|---|---|---|---|
| 349 | 1 dā | tta | 12008 |
| 350 | 2 dā | tta | 12008 |
| 351 | 3 dā | tta | 12008 |
| 249 | jan | janitos, janitvi | 9247 |
| 908 | han | ghata | 8744 |
| 704 | vad | vadita | 3914 |
| 673 | labh | labdhva, labhya | 3345 |
| 911 | 1 hā | hana | 2739 |
| 912 | 2 hā | hana | 2739 |
| 524 | 1 bhuj | bhugna 1 | 2725 |
| 525 | 2 bhuj | bhugna 1 | 2725 |
| 715 | 1 vas | vastave | 2538 |
| 716 | 2 vas | vastave | 2538 |
| 717 | 3 vas | vastave | 2538 |
| 143 | kṣip | ksipita | 2461 |
| 324 | tyaj | tyajita | 2417 |
| 296 | tap | tapita | 2065 |
| 767 | śak | saktave | 1952 |
| 718 | vah | vodha ? E1 | 1845 |
| 469 | 1 pṛ | prta S1. purita | 1512 |
| 470 | 2 pṛ | prta S1. purita | 1512 |
| 471 | 3 pṛ | prta S1. purita | 1512 |
| 262 | juṣ | justvi | 1226 |
| 773 | 1 śam | samita | 1159 |
| 774 | 2 śam | samita | 1159 |
| 775 | 3 śam | samita | 1159 |
| 568 | muh | muhe | 1103 |
| 545 | mad | madita, maditos | 1085 |
| 846 | su | sotave, tos | 878 |
| 19 | av | uta favour, like, delight in | 867 |
| 319 | tṛ | turna | 862 |
| 790 | śuc | sukta ? | 777 |
| 737 | vī | vita 1 | 770 |
| 813 | 1 śrī | sirta | 644 |
| 814 | 2 śrī | sirta | 644 |
| 566 | mud | modam | 612 |
| 534 | bhram | bhramta | 592 |
| 793 | śubh | subhe | 547 |
| 332 | tvar | turta & turna | 539 |
| 899 | sru | sravitave | 538 |
| 99 | kup | kupita RV1 | 521 |
| 772 | śap | sapita | 484 |
| 413 | nad | nadita | 460 |
| 137 | kṣam | ksamta | 439 |
| 119 | kram | kramta | 414 |
| 808 | śram | sramta | 382 |
| 906 | svid | svedam | 369 |
| 343 | dam | danta 1 | 342 |
| 870 | stṛ | startave | 334 |
| 708 | 1 vap | upita E1, vapta E1 | 320 |
| 709 | 2 vap | upita E1, vapta E1 | 320 |
| 576 | mṛj | mrjita, marjita | 298 |
| 719 | 1 vā | vana | 298 |
| 720 | 2 vā | vana | 298 |
| 721 | 3 vā | vana | 298 |
| 743 | vṛj | vrktvi, vrjya | 283 |
| 797 | 1 śṛ | sirta, surta ? RV1 | 278 |
| 798 | 2 śṛ | sirta, surta ? RV1 | 278 |
| 799 | 3 śṛ | sirta, surta ? RV1 | 278 |
| 326 | tras | trasas K | 267 |
| 227 | cit | cite ?, citaye | 266 |
| 649 | riṣ | rise rises | 257 |
| 148 | kṣubh | ksobdhos | 236 |
| 668 | lag | lagna B1.? | 236 |
| 914 | hi | hye | 224 |
| 710 | vam | vamta | 223 |
| 138 | kṣar | ksaradhyai | 220 |
| 706 | van | vata 1 | 220 |
| 635 | 1 rā | ratave | 214 |
| 636 | 2 rā | ratave | 214 |
| 831 | san | sata win, conquer, acquire | 196 |
| 882 | spṛdh | spardhita | 186 |
| 476 | pyā | pyata | 165 |
| 504 | bhakṣ | bhaksita | 162 |
| 567 | muṣ | musta | 162 |
| 209 | ghṛṣ | gharsita | 156 |
| 371 | 1 dṛ | drta R | 151 |
| 372 | 2 dṛ | drta R | 151 |
| 582 | mṛṣ | mrsita | 150 |
| 472 | pṛc | prgna ? RV1, prce | 133 |
| 491 | 1 phal | phalita | 127 |
| 492 | 2 phal | phalita | 127 |
| 417 | nard | nardam | 116 |
| 561 | mī | metos | 103 |
| 661 | ruṣ | rusya | 102 |
| 297 | tam | tamta, tamitos | 99 |
| 552 | 1 mi | mitya | 99 |
| 553 | 2 mi | mitya | 99 |
| 67 | 1 ūh | udha | 98 |
| 68 | 2 ūh | udha | 98 |
| 551 | mārg | margita | 94 |
| 128 | klam | klamta | 90 |
| 263 | jū | javita, javam | 88 |
| 559 | miṣ | misita | 83 |
| 84 | kam | kamta | 82 |
| 365 | du | duta AA. ? C1 | 82 |
| 560 | mih | mihe | 70 |
| 178 | gāh | gahita | 69 |
| 628 | rabh | rabdha | 67 |
| 8 | aṭ | atita | 60 |
| 6 | aj | ajita ? | 55 |
| 322 | tṛṣ | trsita, trsta ? adj | 55 |
| 711 | val | valitva | 54 |
| 747 | vṛh | vrdha brdha | 54 |
| 422 | nāth | nadhita | 52 |
| 878 | spand | spanditum | 52 |
| 633 | ras | rasita 1 | 51 |
| 937 | hvṛ | hvrta, hvarita | 48 |
| 479 | prā | prata | 40 |
| 320 | tṛd | trnna | 39 |
| 900 | svaj | svakta | 39 |
| 344 | day | dayita | 38 |
| 455 | piś | pista | 36 |
| 581 | mṛś | mrsita | 33 |
| 229 | cud | cudita | 31 |
| 224 | cāy | cita | 30 |
| 735 | viṣ | vistvi | 29 |
| 80 | katth | katthita | 28 |
| 932 | hrī | hrina | 28 |
| 727 | vij | vikta | 27 |
| 672 | lap | lapta | 26 |
| 928 | heṣ | hesita | 26 |
| 208 | ghṛ | gharam | 25 |
| 235 | cṛt | crtta | 25 |
| 515 | bhas | bhasita | 25 |
| 185 | gur | gurna | 22 |
| 347 | das | dasta suffer want, languish | 22 |
| 580 | mṛdh | mrddha 1 | 22 |
| 381 | 1 drā | drana | 21 |
| 382 | 2 drā | drana | 21 |
| 804 | śnath | snathas | 21 |
| 751 | vyac | vicita | 20 |
| 323 | tṛh | trdha | 19 |
| 902 | svan | svanita | 19 |
| 765 | vlī | vlina, blina, vliya | 18 |
| 825 | ṣṭhīv | styuta, sthivita | 18 |
| 152 | kṣvid | ksvinna, ksvidas | 17 |
| 333 | tviṣ | tvise | 16 |
| 806 | śrath | srthita, slathita | 16 |
| 62 | ubj | ubjita | 15 |
| 245 | chṛd | chrnna | 15 |
| 13 | am | anta, amita | 14 |
| 803 | ścut | scutita | 13 |
| 936 | hval | hvalita, hvalitos, hvalam | 13 |
| 409 | dhvṛ | dhurta, dhruta, dhurvane | 12 |
| 784 | śiñj | sinjita | 12 |
| 612 | raṃh | ramhita | 11 |
| 87 | kaṣ | kasita, kasam | 10 |
| 619 | raṭ | ratita | 10 |
| 299 | tarj | tarjita | 9 |
| 583 | med | minna | 9 |
| 10 | at | atita | 8 |
| 366 | dudh | dudhita | 8 |
| 725 | 1 vic | vikta | 8 |
| 726 | 2 vic | vikta | 8 |
| 241 | chā | chita | 7 |
| 288 | tak | tankam | 7 |
| 306 | tim | timita R | 7 |
| 683 | liś | lista | 7 |
| 74 | ṛd | ardita = | 6 |
| 511 | bharts | bhartsita | 6 |
| 556 | mith | mithita | 6 |
| 660 | rup | rupita | 6 |
| 805 | śyā | sita, sina | 6 |
| 824 | śvit | svitta | 6 |
| 929 | hnu | hnuta | 6 |
| 100 | kuṣ | kusita pinch, tear, gnaw | 5 |
| 2 | 1 akṣ | asta | 4 |
| 3 | 2 akṣ | asta | 4 |
| 50 | īrṣy | irsyita | 4 |
| 63 | ubh | umbhita | 4 |
| 105 | kūrd | kurdita | 4 |
| 230 | cup | cupita | 4 |
| 290 | tañc | takta | 3 |
| 589 | mruc | mrukta, mlukta, mlupta | 3 |
| 877 | snu | snuta ? | 3 |
| 935 | hlād | hlanna | 3 |
| 202 | ghaṭṭ | ghattita | 2 |
| 460 | pīḍ | pidita | 2 |
| 585 | mnā | mnata | 2 |
| 594 | mlech | mlechita, mlista | 2 |
| 601 | yas | yasta, yasita | 2 |
| 648 | riś | rista | 2 |
| 778 | śas | sasta | 2 |
| 916 | hikk | hikkita | 2 |
| 934 | hreṣ | hresita | 2 |
| 86 | kal | kalita | 1 |
| 101 | kū | kuta, kavam | 1 |
| 140 | kṣā | ksana ? | 1 |
| 182 | guṇṭh | gunthita veil, conceal, hide | 1 |
| 429 | 1 nu | nuta | 1 |
| 430 | 2 nu | nuta | 1 |
| 573 | mṛkṣ | mraksita = seq. abhi | 1 |
| 574 | mṛc | mrkta | 1 |
| 646 | riph | riphita | 1 |
| 859 | sku | skuta, skavam | 1 |
| 9 | aṇṭh | anthita | 0 |
| 88 | kas | kasta, kasita | 0 |
| 103 | kūḍ | kulita | 0 |
| 168 | gadh | gadhita RV2 | 0 |
| 219 | cam | camta | 0 |
| 284 | ḍī | dina | 0 |
| 493 | baṃh | badha | 0 |
| 563 | mīv | muta | 0 |
| 590 | mreḍ | mredita | 0 |
| 677 | laṣ | lasita | 0 |
| 809 | śrambh | srabdha | 0 |
| 931 | hrād | hradita | 0 |

_Dr. Mārcis Gasūns_
