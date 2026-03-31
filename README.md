# Educational NMT (exam) Data Analysis 2022-2025 in Ukraine

## Setup
Dataset has been pushed through [git-lfs](https://git-lfs.com/). This is official dataset for the real exam data for schoold graduates. If it doesn't work, dataset can be downloaded year-by-year from [here](https://zno.testportal.com.ua/opendata), put into **"data"** directory and named `f"Odata{year}file.csv"`, where year stands for year (2022, 2023...)

## Problem 1: Determine the best school and explain criteria

To determine the best school they were split into few categories: humanities, tech and overall. Where tech = [math, physics, chemistry, biology], humanities = [languages, literature, geography]. Score that was used to determine - average score per categories, with enforced constraints (each year >10 students)

### Challenges
- Schools can have unsignificant amount of graduates (<10)
- Schools amount of graduates fluctuates on a yearly bases (8, 12, 15)
- Schools might not have entries for people who took certain subjects

### The results

#### Top schools, assuming criteria >10 students in each year, scores averaged
![top_schools_trend_all subjects.png](/plots%2Fhomework%2Fprogression%2Ftop_schools_trend_all%20subjects.png)
![top_schools_trend_tech.png](/plots%2Fhomework%2Fprogression%2Ftop_schools_trend_tech.png)
![top_schools_trend_humanities.png](/plots%2Fhomework%2Fprogression%2Ftop_schools_trend_humanities.png)

#### Top Schools by Average Score (All Subjects)

| Заклад освіти | Avg Score | Students |
|---|---:|---:|
| Львівський фізико-математичний ліцей-інтернат п... | 179.412719 | 570 |
| Природничо-науковий ліцей №145 Печерського райо... | 174.845129 | 219 |
| Львівська гімназія "Євшан" | 174.468027 | 245 |
| Технічний ліцей Національного технічного універ... | 173.209851 | 357 |
| Львівська академічна гімназія при Національному... | 173.088731 | 386 |
| Заліщицька державна гімназія м.Заліщики Тернопі... | 171.203959 | 181 |
| Класична гімназія при Львівському національному... | 170.391150 | 258 |
| Черкаський фізико-математичний ліцей (ФІМЛІ) Че... | 169.477709 | 243 |
| Чернівецький ліцей №1 математичного та економіч... | 168.779707 | 216 |
| Ліцей №8 Львівської міської ради | 167.534910 | 148 |


#### Top Schools by Average Score (Humanities)

| Заклад освіти | Avg Score | Students |
|---|---:|---:|
| Львівський фізико-математичний ліцей-інтернат п... | 177.456433 | 570 |
| Львівська гімназія "Євшан" | 174.278231 | 245 |
| Львівська академічна гімназія при Національному... | 172.653282 | 386 |
| Заліщицька державна гімназія м.Заліщики Тернопі... | 172.039595 | 181 |
| Класична гімназія при Львівському національному... | 171.963178 | 258 |
| Природничо-науковий ліцей №145 Печерського райо... | 171.261796 | 219 |
| Український гуманітарний ліцей Київського націо... | 170.737374 | 264 |
| Ліцей №8 Львівської міської ради | 170.045045 | 148 |
| Технічний ліцей Національного технічного універ... | 169.951914 | 357 |
| Бердичівська міська гуманітарна гімназія №2 | 168.331395 | 86 |

#### Top Schools by Average Score (Tech)

| Заклад освіти | Avg Score | Students |
|---|---:|---:|
| Львівський фізико-математичний ліцей-інтернат п... | 183.642105 | 570 |
| Природничо-науковий ліцей №145 Печерського райо... | 180.949772 | 219 |
| Технічний ліцей Національного технічного універ... | 179.661064 | 357 |
| Львівська гімназія "Євшан" | 175.195918 | 245 |
| Черкаський фізико-математичний ліцей (ФІМЛІ) Че... | 175.022634 | 243 |
| Чернівецький ліцей №1 математичного та економіч... | 174.953704 | 216 |
| Львівська академічна гімназія при Національному... | 173.778497 | 386 |
| Заліщицька державна гімназія м.Заліщики Тернопі... | 169.378453 | 181 |
| Класична гімназія при Львівському національному... | 166.408915 | 258 |
| Волинський науковий ліцей Волинської обласної ради | 166.272727 | 242 |


### Conclusions:

According to the selected metrics, the best school is 'Львівський фізико-математичний ліцей...'. However, the fact should be taken into the account that there are schools with better scores, but they have less graduates. The examples are "Prestige lyceum" and "Rusanivskyi lyceum"

## Problem 2. City vs. Village (IFE) Performance Gap

### Problem Statement
Identify if there is a divergence between city and rural area over the time

### Challenges
- Category regrouping, (Селище, село)
- New countries were added in the middle

### The Results
- **City (Місто):** Average score of 141.66 (over years)
- **Village/Rural (Селище, село):** Average score of 136.06 (over years)

#### Urban vs rural gap. Averaged 2022 - till present
![urban_rural_gap.png](/plots%2Fhomework%2Fprogression%2Furban_rural_gap.png)
![urban_vs_rural.png](/plots%2Fhomework%2Fprogression%2Furban_vs_rural.png)

The biggest gap spotted was in 2023, which might be explained by intense migration from the combar zone into the city

## Problem 3. Patterns In Examination Subject Choices for Men and Women

### Problem Statement
Investigate whether there are distinct gender-based patterns in choosing elective examination subjects.

### Investigation Results 
To ensure accurate assessment, we intentionally excluded the core mandatory subjects (Mathematics, Ukrainian Language, History) since universal participation skews preference-based metrics. Instead, we analyzed the remaining test subjects, evaluating participation ratios per pool (`male_%` out of all males, vs `female_%` out of all females).

Our analysis highlights major discrepancies:
- **Strong Male Skew:** **Physics (Фізика)** and **Geography (Географія)** show a massive male preference. A male student is roughly 5.7 times more likely to voluntarily choose Physics compared to a female student. Geography shows a 2.1x male bias.
- **Strong Female Skew:** **Biology (Біологія)**, **Ukrainian Literature**, and specialized foreign languages like French/Spanish are heavily female-dominated. For example, 24% of female students elect to take Biology compared to only 14.7% of male students. Ukrainian Literature shows an extreme disparity

---
*Note: The corresponding data visualizations—showing score progression over the years, subject difficulties, and detailed gender histogram bars—are automatically generated by the analysis pipeline and stored in the `plots/` directory.*

#### Gender bias 2024
![gender_bias_2024.png](/plots%2Fhomework%2Fgender%2Fgender_bias_2024.png)

#### Gender bias 2025
![gender_bias_2025.png](/plots%2Fhomework%2Fgender%2Fgender_bias_2025.png)

#### Gender bias overall averaged (since 2022)
![gender_bias_overall.png](/plots%2Fhomework%2Fgender%2Fgender_bias_overall.png)

#### Gender bias by subject, 2024, 2025 and overall
![gender_subject_distribution_2024.png](/plots%2Fhomework%2Fgender%2Fgender_subject_distribution_2024.png)
![gender_subject_distribution_2025.png](/plots%2Fhomework%2Fgender%2Fgender_subject_distribution_2025.png)
![gender_subject_distribution_overall.png](/plots%2Fhomework%2Fgender%2Fgender_subject_distribution_overall.png)

## Gender Score Distribution (Candle / Boxplot)

### Problem statement
Analysis if one gender performs better compared to the other oen

### The results
Based on the data, we can see, that girls perform better in 2/3 mandatory subjects (history and Ukrainian language). What is interesting, girls outperform in physics, though, we know gender bias is skewed for males. We can make conclusions that girls are the gender that raises overall score (due to heavy impact for base subjects)

#### Chart per subj per gender overall for all years
![gender_candle_overall.png](/plots%2Finvestigation%2Fgender%2Fgender_candle_overall.png)

#### Chart per subj per gender overall for 2025
![gender_candle_2025.png](/plots%2Finvestigation%2Fgender%2Fgender_candle_2025.png)

## Math results analysis

### Problem statement
Analyze the results for mathematics scores and it's distribution (believed to be the subject heavily correlated with other technical ones) per year

### The results
We are seeing that at the 2022 the results were moderate, more looking like a normally distributed around the 150-160. 2023-2025 we are seeing that distribution is significantly skewed to the left, with growing bars closer to 2025. We can conclude that overall results have significantly degraded and it's expected to become a new "reality" in few years to score 140 and consider this a great results

### Score distribution charts 2022-2025

![Математика.png](/plots%2Finvestigation%2Fdistributions%2F2022%2F%D0%9C%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0.png)
![Математика.png](/plots%2Finvestigation%2Fdistributions%2F2023%2F%D0%9C%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0.png)
![Математика.png](/plots%2Finvestigation%2Fdistributions%2F2024%2F%D0%9C%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0.png)
![Математика.png](/plots%2Finvestigation%2Fdistributions%2F2025%2F%D0%9C%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0.png)

## General conclusion

- Top-tier education is highly concentrated in a small number of elite institutions. Lviv, Kyiv cities
- Urban advantage is persistent and structural 
- Gender differences are behavioral (choice) and performance-based 
- Mathematics (and other tech subjects) are the most concerning weak points and expected to degrade further
