import re
import cv2
import easyocr

# commit msg: adapt ocr and flight no functionality from streamlit

img = Image.open(uploaded_file)
            # Converts PIL image to OpenCv
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            # Display scaled image if size is too large
            st.text("Uploaded Image:")
            if img.shape[0] > 600 or img.shape[1] > 600:
                w, h, c = img.shape
                sf = 400 / w
                img2 = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
                                None, fx=sf, fy=sf, interpolation=cv2.INTER_AREA)
                st.image(img2)
            else:
                st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            display_fun_facts()

            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            reader = easyocr.Reader(["en"], gpu=True)
            text_list = list(reader.readtext(img, detail=0))

            # Remove Duplicates
            list_without_duplicates = []
            for code in text_list:
                if code not in list_without_duplicates:
                    list_without_duplicates.append(code)

            # list_without_duplicates
            for code in list_without_duplicates:
                code = code.upper()
                # Substitute underscores for hyphens
                code = code.replace("_", "-")
                # Remove all characters that are not hyphens or alphanumeric
                code_with_only_alphanumeric_characters_and_hyphens = re.sub(
                    "[^\w-]", "", code)
                # Possible prefixes without hyphens: "HL, N, UK, JA, UR(with or without), HI"
                pattern = r"\w{1,4}-\w+|HL\w{4}|N\d{1,3}\w{2}|N\d{1,5}|UK\d{5}|JA\w{4}|UR\d{5}|HI\w{3,4}"
                matches = re.findall(
                    pattern, code_with_only_alphanumeric_characters_and_hyphens)
                if len(matches) > 0:
                    if len(matches[0]) == len(code):
                        aircraft_details_query(code)
                        st.markdown("---")

        if aircraft_code == "" and uploaded_file is None:
            st.markdown(
                "#### Please enter a valid aircraft registration number or upload an image.")