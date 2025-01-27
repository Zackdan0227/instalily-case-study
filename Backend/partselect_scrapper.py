import undetected_chromedriver as uc
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_partselect(url):
    """
    Uses a stealth ChromeDriver to bypass bot detection and scrape product details from PartSelect.
    Returns structured JSON data.
    """

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent detection
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")  # Start maximized to ensure all elements are visible

    driver = uc.Chrome(options=options, headless=False)  # Set headless=True for production

    
    driver.get(url)
    wait = WebDriverWait(driver, 15)  # Increased wait time for dynamic content

    try:
        decline_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='reset' and @data-click='close']")))
        decline_button.click()
        time.sleep(2)  # Allow time for popup to close
    except Exception as e:
        print(f"⚠️ No popup detected or failed to close: {e}")

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    product_data = {}
    try:
        main_div = driver.find_element(By.ID, "main")
        product_data.update({
            "inventory_id": main_div.get_attribute("data-inventory-id"),
            "description": main_div.get_attribute("data-description"),
            "price": main_div.get_attribute("data-price"),
            "brand": main_div.get_attribute("data-brand"),
            "model_type": main_div.get_attribute("data-modeltype"),
            "category": main_div.get_attribute("data-category"),
        })
    except Exception as e:
        print(f"⚠️ Basic product info extraction failed: {e}")
        product_data = {"error": "No product details found."}

    product_description = "No description available."
    try:
        # Ensure the Product Description section is expanded
        description_header = driver.find_element(By.ID, "ProductDescription")
        driver.execute_script("arguments[0].scrollIntoView();", description_header)
        if description_header.get_attribute("aria-expanded") == "false":
            description_header.click()
            time.sleep(2)  # Allow time for expansion

        description_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@itemprop='description']")))
        product_description = description_element.text.strip()
    except Exception as e:
        print(f"⚠️ Product Description extraction failed: {e}")

    troubleshooting_info = {}
    try:
        troubleshooting_header = driver.find_element(By.ID, "Troubleshooting")
        driver.execute_script("arguments[0].scrollIntoView();", troubleshooting_header)
        if troubleshooting_header.get_attribute("aria-expanded") == "false":
            troubleshooting_header.click()
            time.sleep(2)  # Allow time for expansion

        troubleshooting_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@id='Troubleshooting']/following-sibling::div")))
        raw_text = troubleshooting_element.text.strip()

        troubleshooting_info = {}

        # Split into lines
        lines = raw_text.split('\n')

        symptoms = []
        products = []
        replacements = []

        # Parse each line
        for i in range(len(lines)):
            line = lines[i].strip()
            if line.startswith("This part fixes the following symptoms:"):
                symptoms = lines[i + 1].split(" | ")  # Extract symptoms
            elif line.startswith("This part works with the following products:"):
                products = lines[i + 1].split(" | ")  # Extract products
            elif line.startswith("Part#"):
                replacements = lines[i + 1].split(", ")  # Extract replacements

        # Remove empty entries
        troubleshooting_info = {
            "symptoms": [s.strip() for s in symptoms if s.strip()],
            "products": [p.strip() for p in products if p.strip()],
            "replacements": [r.strip() for r in replacements if r.strip()]
        }

    except Exception as e:
        print(f"⚠️ Troubleshooting Info extraction failed: {e}")
        troubleshooting_info = "No troubleshooting info available."

    model_compatibility = []
    try:
        model_compatibility_header = driver.find_element(By.ID, "ModelCrossReference")
        driver.execute_script("arguments[0].scrollIntoView();", model_compatibility_header)
        if model_compatibility_header.get_attribute("aria-expanded") == "false":
            model_compatibility_header.click()
            time.sleep(2)  # Allow time for expansion

        model_compatibility_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@id='ModelCrossReference']/following-sibling::div")))
        model_compatibility_text = model_compatibility_element.text.strip()

        # Parse Model Compatibility into a list of dictionaries
        lines = model_compatibility_text.split('\n')

        # Identify the start of model data by finding the line after headers
        try:
            headers_index = lines.index("Description")
            data_lines = lines[headers_index + 1:]
        except ValueError:
            # If "Description" is not found, assume data starts after first 3 lines
            data_lines = lines[3:] if len(lines) > 3 else []

        # Iterate through the data in chunks of 3 lines (Brand, Model Number, Description)
        for i in range(0, len(data_lines), 3):
            try:
                brand = data_lines[i].strip()
                model_number = data_lines[i + 1].strip()
                description = data_lines[i + 2].strip()

                # Skip if any field is missing
                if not brand or not model_number or not description:
                    continue

                # Clean up description
                description = description.replace("- REFRIGERATOR", "").strip()

                model_compatibility.append({
                    "brand": brand,
                    "model_number": model_number,
                    "description": description
                })
            except IndexError:
                # Incomplete data; skip
                continue

    except Exception as e:
        print(f"⚠️ Model Compatibility extraction failed: {e}")
        model_compatibility = "No model compatibility listed."
    
    qna = []
    try:
        # Ensure the Q&A section is expanded
        qna_header = driver.find_element(By.ID, "QuestionsAndAnswers")
        driver.execute_script("arguments[0].scrollIntoView();", qna_header)
        if qna_header.get_attribute("aria-expanded") == "false":
            qna_header.click()
            time.sleep(2)  # Allow time for expansion

        # Wait for Q&A content to load
        qna_container = wait.until(EC.presence_of_element_located(
            (By.ID, "QuestionsAndAnswersContent")))
        
        # Function to extract Q&A from the current page
        def extract_qna_from_page():
            qna_elements = qna_container.find_elements(By.CLASS_NAME, "qna__question")
            for qna_element in qna_elements:
                try:
                    # Extract question
                    question_text_element = qna_element.find_element(By.CLASS_NAME, "js-searchKeys")
                    question_text = question_text_element.text.strip()

                    # Extract answer
                    answer_element = qna_element.find_element(By.CSS_SELECTOR, "div.qna__ps-answer__msg > div.js-searchKeys")
                    answer_text = answer_element.text.strip()

                    qna.append({
                        "question": question_text,
                        "answer": answer_text
                    })
                except Exception as e:
                    print(f"⚠️ Failed to extract a Q&A pair: {e}")
                    continue

        # Extract Q&A from the first page
        extract_qna_from_page()

        # Handle pagination (if multiple pages exist)
        page_number = 1
        max_pages = 10  # Prevent infinite loops

        while page_number < max_pages:
            try:
                # Get the first question's text to detect page change
                first_qna_element = qna_container.find_element(By.CLASS_NAME, "qna__question")
                first_question_text = first_qna_element.find_element(By.CLASS_NAME, "js-searchKeys").text.strip()

                # Find the 'Next' button within the current Q&A container using flexible XPath
                next_button = qna_container.find_element(By.XPATH, ".//ul[contains(@class, 'pagination') and contains(@class, 'js-pagination')]//li[contains(@class, 'next')]")
                
                # Check if 'Next' button is disabled
                if "disabled" in next_button.get_attribute("class"):
                    break
                else:
                    # Click the 'Next' button
                    next_button.click()

                    # Wait for the first question's text to change, indicating a new page
                    wait.until(lambda d: qna_container.find_element(By.CLASS_NAME, "qna__question").find_element(By.CLASS_NAME, "js-searchKeys").text.strip() != first_question_text)
                    
                    # Small delay to ensure content has loaded
                    time.sleep(1)

                    # Extract Q&A from the new page
                    extract_qna_from_page()
                    page_number += 1
            except Exception as e:
                print(f"⚠️ Pagination handling failed or no more pages: {e}")
                break


    except Exception as e:
        print(f"⚠️ Q&A extraction failed: {e}")
        qna = "No Q&A available."

    product_data.update({
        "full_description": product_description,
        "troubleshooting_info": troubleshooting_info,
        "model_compatibility": model_compatibility,
        "qna":qna,
        "product_page": url
    })

    return product_data



if __name__ == "__main__":
    test_url = "https://www.partselect.com/PS11752778-Whirlpool-WPW10321304-Refrigerator-Door-Shelf-Bin.htm"
    extracted_data = scrape_partselect(test_url)

    print(json.dumps(extracted_data, indent=4))
