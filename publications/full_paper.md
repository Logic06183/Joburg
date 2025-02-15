# Quantifying intra-urban socio-economic and environmental vulnerability to extreme heat events in Johannesburg, South Africa

## Authors

Craig Parker¹*, Craig Mahlasi², Tamara Govindasamy², Lebohang Radebe¹, Nicholas Brian Brink¹, Christopher Jack³, Madina Doumbia⁴, Etienne Kouakou⁵, Matthew Chersich¹, Gueladio Cisse⁴, Sibusisiwe Makhanya², for the HE²AT Center Group

## Affiliations

1. Wits Planetary Health Research, Faculty of Health Sciences, University of the Witwatersrand, Johannesburg, South Africa
2. IBM Research - Africa, South Africa
3. Climate System Analysis Group, University of Cape Town, South Africa
4. University Peleforo Gon Coulibaly, Côte d'Ivoire
5. Centre Suisse de Recherches Scientifiques, Côte d'Ivoire

## Abstract

Urban populations face increasing vulnerability to extreme heat events, particularly in rapidly urbanising Global South cities where environmental exposure intersects with socioeconomic inequality and limited healthcare access. This study quantifies heat vulnerability across Johannesburg, South Africa, by integrating high-resolution environmental data with socio-economic and health metrics across 135 urban wards. We examine how historical urban development patterns influence contemporary vulnerability distributions using principal component analysis and spatial statistics.

Environmental indicators (Land Surface Temperature(LST), vegetation indices, and thermal field variance) were combined with socioeconomic variables (including crowded dwellings and healthcare access) and health metrics (prevalence of chronic diseases) in a comprehensive vulnerability assessment. Principal component analysis revealed three primary dimensions explaining 56.6% (95% CI: 52.4-60.8%) of the total variance: urban heat exposure (31.5%), health status (12.8%), and socio-economic conditions (12.3%). Built-up areas showed weak but significant correlations with heat indices (ρ = 0.28, p < 0.01), while higher poverty levels demonstrated moderate positive correlations with LST (ρ = 0.41, p < 0.001).

Spatial analysis identified significant clustering of vulnerability (Global Moran's I = 0.42, p < 0.001), with high-vulnerability clusters concentrated in historically disadvantaged areas. These clusters exhibited limited healthcare access (mean travel time to facilities >45 minutes) and elevated environmental exposure (mean LST 2.3°C above ward average). Integration of historical planning data revealed persistent patterns of environmental inequality, with pre-1994 township areas showing significantly higher vulnerability scores (p < 0.001).

These findings demonstrate how historical planning decisions continue to shape contemporary environmental health risks, with vulnerability concentrated in areas of limited healthcare access and high extreme heat exposure. Results suggest the need for targeted interventions that address both environmental and social dimensions of heat vulnerability, particularly focusing on expanding healthcare access in identified hotspots and implementing community-scale green infrastructure in high-risk areas. This study provides an evidence-based framework for prioritising heat-resilience initiatives in rapidly urbanising Global South cities while highlighting the importance of addressing historical inequities in urban adaptation planning.

## Keywords

Urban Heat Vulnerability, Spatial Analysis, Healthcare Access, Environmental Justice, Climate Adaptation, Principal Component Analysis, Johannesburg, Environmental Health

## Statements and Declarations

### Acknowledgement

The research was conducted as part of the HE²AT and Health in Africa Transdisciplinary (HEAT) Center initiative, supported by the NIH Common Fund under Award Number U54 TW 012083. We acknowledge the valuable contributions of the HE²AT Center Group, which includes researchers, collaborators, and supporting staff from partner institutions.... Their collective efforts in data sharing, technical support, and capacity building have significantly advanced this research.

We also extend our gratitude to the data owners and contributors who shared their datasets, enabling this study to integrate environmental, socioeconomic, and health metrics. Special thanks go to the Gauteng City-Region Observatory (GCRO) for providing the Quality of Life Survey data and to the United States Geological Survey for Landsat 8 satellite imagery.

Finally, we are grateful for the administrative and technical support provided by the HE²AT Center Steering Committee and partner institutions and the guidance and input from the Publications Group. This publication reflects the authors' views and not necessarily those of the NIH or other supporting organisations.

### Ethics Approval and Consent

This research was conducted with approval from the Wits Human Research Ethics Committee in Johannesburg (reference number 200606). The study utilised secondary data analysis of publicly available datasets and followed the United States Department of Health and Human Services regulations for protecting human research subjects (45 CFR 46). All data were anonymised and processed in accordance with ethical research principles.

Not applicable - this study used secondary data analysis of publicly available datasets and did not involve direct human participants.

### Data Availability

The datasets analysed during the current study are available from the following sources:

- Environmental metrics were derived from ERA5 reanalysis data and Landsat 8 satellite imagery (December-February 2020-2021), available from the United States Geological Survey [Earth Explorer](https://earthexplorer.usgs.gov/)
- Socio-economic and health data were obtained from the Gauteng City-Region Observatory (GCRO) Quality of Life Survey 2020-2021
- Analysis scripts and processed data are available from the corresponding author upon request

### Author Contributions

**Conceptualisation:** Craig Parker, Craig Mahlasi, Tamara Govindasamy, Matthew Chersich and Sibusisiwe Makhanya conceived and designed the study.

**Final approval:** All authors reviewed and approved the final manuscript.

### Competing Interests

**Financial interests:** Authors affiliated with Wits Planetary Health Research declare no competing financial interests.

## Introduction

Climate change is significantly reshaping urban life, with extreme heat events becoming more frequent and severe \[[1](#_ENREF_1), [2](#_ENREF_2)\]. Urban populations face increasing vulnerability to these events, with risks shaped by complex interactions between environmental exposure, socioeconomic conditions, and health status \[[3](#_ENREF_3), [4](#_ENREF_4)\]. This vulnerability is particularly acute in rapidly urbanising Global South cities, where historical inequalities and limited adaptive capacity compound environmental challenges\[[5](#_ENREF_5), [6](#_ENREF_6)\].

Johannesburg, South Africa's largest city with 6.1 million inhabitants, presents a compelling case study of urban heat vulnerability\[[7](#_ENREF_7)\]. The city's rapid urbanisation, pronounced socio-economic inequalities, and historical legacy of apartheid urban planning create distinct patterns of environmental risk\[[8](#_ENREF_8), [9](#_ENREF_9)\]. These factors interact with the urban heat island effect to produce heterogeneous vulnerability landscapes, particularly affecting disadvantaged populations \[[10](#_ENREF_10)\]. Understanding these patterns is crucial for developing effective adaptation strategies, yet comprehensive analyses of urban heat vulnerability in African cities remain limited\[[2](#_ENREF_2)\].

## Methods

### 9.1 Data Collection and Processing

We integrated environmental, socio-economic, and health data to assess heat vulnerability across Johannesburg's 135 wards. Environmental metrics were derived from ERA5 reanalysis data and Landsat 8 satellite imagery (December-February 2020-2021), selected for minimal cloud cover (<10%)\[[24](#_ENREF_24)\].

Land Surface Temperature (LST) and vegetation indices were calculated using Google Earth Engine. The Normalized Difference Vegetation Index (NDVI) provided vegetation coverage estimates, the Urban Thermal Field Variance Index (UTFVI) provided relative heat intensity measures, and the Normalized Difference Built-up Index (NDBI) quantified urban density.

### 9.2 Analytical Methods

Principal Component Analysis (PCA) was employed to identify key dimensions of heat vulnerability. Variables were standardized prior to analysis, and component selection was based on eigenvalues >1.0 and scree plot examination.

## Results

### 10.1 Principal Component Analysis

Principal Component Analysis identified three significant components explaining 56.6% (95% CI: 52.4-60.8%) of total variance. The first component accounted for 31.5% of the variance (eigenvalue = 4.73), with the strongest loadings from environmental variables.

### 10.2 Spatial Patterns

The spatial analysis identified significant clustering of vulnerability (Global Moran's I = 0.42, p < 0.001), with distinct high-vulnerability clusters in historically disadvantaged areas.

### 10.3 Correlation Analysis

Examination of Spearman rank correlations revealed several notable associations between socioeconomic indicators and environmental exposures (Table 5). Vegetation cover (NDVI) showed significant negative correlations with household overcrowding (ρ=-0.56, p<0.001) and food insecurity (ρ=-0.58, p<0.001).

## Discussion

### 11.1 Key Findings

Our findings reveal how urban heat vulnerability in Johannesburg manifests through a complex interplay of environmental exposure, socio-economic conditions, and healthcare access.

### 11.2 Implications

These results have important implications for urban planning and public health interventions:

- First, they highlight the need for targeted interventions in high-vulnerability clusters
- Second, they demonstrate the importance of integrating healthcare access into heat vulnerability assessments
- Third, they suggest potential entry points for breaking the cycle of environmental health inequity

### 11.3 Limitations

Although the GCRO Quality of Life Survey provides a rich dataset for exploring urban vulnerabilities, it has some constraints:

- The survey is not primarily designed as a health assessment
- Some indicators rely on self-reported data
- The temporal resolution of environmental data is limited

## Tables

Table 1. Summary of Environmental, Socioeconomic, and Health Indicators Across Johannesburg Wards (N=135)

{{ ... }}

## References

{{ ... }}

## Figures

![Figure 1: Analytical Framework](media/media/image2.svg)

![Figure 2: Heat Vulnerability Index map](media/media/image3.png)

![Figure 3: High vulnerability clusters](media/media/image4.png)

![Figure 4: LISA clustering analysis](media/media/image5.png)

## Appendices

### A.1 Additional Analysis Results

![Figure A1: Socioeconomic patterns](media/media/image6.png)

![Figure A2: Temporal trends](media/media/image7.png)

![Figure A3: Intervention framework](media/media/image8.png)

![Figure A4: Vulnerability components](media/media/image9.png)

![Figure A5: Monitoring framework](media/media/image10.png)

![Figure A6: Evaluation framework](media/media/image11.png)
