# SmartHeathAI
### Your Digital Health Companion for Early Diagnosis and Better Care

## Inspiration
The inspiration for Smart Health AI came from recognizing the overburdened healthcare system, lack of personalized patient care, diagnostic errors due to incomplete information, high healthcare costs, and delays in early diagnosis. By providing an accessible, AI-driven platform for early diagnosis and personalized health management, Smart Health AI aims to reduce healthcare burdens, improve diagnostic accuracy, and encourage timely medical intervention, making healthcare more efficient and affordable.

## What it does?
- **Data Collection:**
  - Clinical text data (symptoms, treatments, medications)
  - Patient images analyzed using the gemini-1.5-pro-latest model
  - Lab reports extracted from PDFs using PyPDF2
    
- **Data Processing:**
  - Combines text, image, and lab data into a comprehensive dataset
  - De-identifies patient data for privacy
  - Uses Amazon Comprehend Medical for structured clinical data extraction

- **Diagnosis and Suggestions:**
  - AI-driven diagnosis of potential health issues
  - Provides personalized dietary, exercise, and lifestyle recommendations

- **PDF Report Generation:**
  - Converts detailed clinical data and AI insights into a downloadable PDF using ReportLab

- **Retrieval-Augmented Generation (RAG) Integration:**
  - Enhances user interaction using generated PDF
  - Employs LlamaIndex and gemini for advanced information retrieval and generation
  - Provides personalized responses based on patient data, improving engagement and usability
  - This is useful for efficient data retrieval, evidence-based recommendation and help in personalised medical assistance.

- **Nutritional Analysis:**
  - Integrated with Edamam API for nutritional content analysis
  - Generates personalized recipes based on patient data and preferences using the power of RAG and Edamam API.

