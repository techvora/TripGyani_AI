import base64
import logging
import textwrap
import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF
from groq import Groq, BadRequestError
import json
import requests
from wikipedia import get_wikipedia_image_for_specific_destination

# Configure logging to output to the terminal
logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format for log messages
    handlers=[logging.StreamHandler()]  # Use StreamHandler to log to the terminal
)


def tripgenie():

# ==================================== Page Configration, Image Encoding & User Inputs =================================================================

    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    # STORE FAVICON PNG IMAGE LOGO IN VARIABLE
    favicon_path = "images/Yellow_Favicon.png"
    bg_image_base64 = get_base64_image("images/top-view.jpg")

    flag = False

    # STORE LOGO FILE PATH IN VARIABLE AND USE IT TO SET ON MAIN PAGE
    logo_path = "images/Inexture_logo_2023.png"

    st.logo(logo_path, icon_image=logo_path)

    # SET STREAMLIT APP TITLE AND GET USER INPUT
    st.title("Trip Genie!")

    with st.container():
        destination = st.text_input("Destination", placeholder="Enter Destination", )

    col1, col2 = st.columns([1, 1])
    with col1:
        day = st.number_input("Days", value=1, min_value=1, max_value=10)

    with col2:
        travel_type = st.selectbox('Travel Type', ('Solo', 'Couple', 'Family', 'Friend'), index=None,
                                   placeholder="Select style")


# ==================================== LLM Model =================================================================

    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY")) # for gemini_llm_model

    # CREATE FUNCTION FOR LLM MODEL
    def groq_llm_model(prompt):
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            response_format={"type": "json_object"}
        )
        response = chat_completion.choices[0].message.content
        return response

    def google_llm_model(prompt):
        try:
            model = genai.GenerativeModel(model_name='gemini-1.5-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error occurred {e}"


# ==================================== PDF Format =================================================================


    # CREATE FUNCTION TO DOWNLOAD PDF
    def add_header(pdf):
        """Function to add header on each page"""
        pdf.image("images/Inexture_logo_2023.png", x=None, y=None, w=60, h=10, type='', link='')
        pdf.set_font("arial", "B", size=25)
        pdf.text(x=155.0, y=18.5, txt="Trip Genie")
        pdf.set_font("arial", size=10)
        pdf.text(x=117.0, y=24.5, txt="Travel and Tourism with Personalized AI Assistance")

        pdf.set_line_width(width=2.0)
        pdf.set_draw_color(r=251, g=169, b=30)
        pdf.line(x1=0.0, y1=28.5, x2=250, y2=28.5)


    def json_to_pdf(n_data, days, destination, travel_type):
        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        pdf.set_font("Arial", "B", size=25)

        add_header(pdf)

        pdf.set_font("Arial", "B", size=12)
        if isinstance(n_data, dict) and 'days' in n_data and isinstance(n_data['days'], list):
            # Travel details
            pdf.text(x=10.0, y=40.0, txt="Days: " + str(days))
            pdf.text(x=80.0, y=40.0, txt="Destination: " + str(destination))
            pdf.text(x=160.0, y=40.0, txt="Travel Type: " + str(travel_type))

            # Horizontal line separator
            pdf.set_line_width(width=0.010)
            pdf.set_draw_color(r=0, g=0, b=0)
            pdf.line(x1=10.0, y1=45.0, x2=200, y2=45.0)

            current_x = 10.0
            current_y = 50.0

            for day_index, day in enumerate(n_data['days']):
                if day_index > 0:  # Check if it's not the first day
                    pdf.add_page()
                    add_header(pdf)  # Add header for new page
                    current_y = 35  # Reset Y position for new page

                pdf.set_x(current_x)
                pdf.set_y(current_y)

                # Title for the day
                pdf.set_font("Arial", "B", size=25)
                pdf.multi_cell(200, 15, txt=f"Day {day['day']}", align="L")
                current_y += 10  # Space for the day title

                for i, activity in enumerate(day['activities'], start=1):
                    for key, value in activity.items():
                        if key == "title":
                            pdf.set_font("Arial",  size=14)
                            pdf.multi_cell(180, 12, txt=f"{i}. {value.capitalize()}", align="L")
                            current_y += 12  # Space for the activity title

                        if key == "link" and value != "":
                            pdf.set_font("Arial", size=10)
                            pdf.set_text_color(0, 0, 0)  # Set text color to black
                            pdf.cell(30, 5, "Google map:", align="L")
                            pdf.set_text_color(0, 0, 255)  # Set link color to blue
                            pdf.cell(0, 5, value, link=value)
                            pdf.ln()
                            current_y += 5  # Space for the link
                        else:
                            if key.lower() != "title" and value != "" and key.lower() != "approx cost" and key.lower() != "restaurants" and key.lower() != "restaurant":
                                pdf.set_font("Arial", size=10)
                                pdf.set_text_color(0, 0, 0)  # Reset text color to black
                                pdf.set_x(current_x)
                                pdf.cell(30, 5, f"{key.capitalize()}:", align="L")

                                wrapped_text = textwrap.fill(str(value), width=180)
                                for line in wrapped_text.split('\n'):
                                    pdf.set_x(current_x + 30)
                                    pdf.multi_cell(150, 5, line)

                                current_y += (len(wrapped_text.split('\n')) * 5) + 2  # Adjust y position

                # Add minimum space between days
                current_y += 5  # Minimum space before the next day

        return pdf.output(dest='S')


# ==================================== JValidation, Custom_Error =================================================================


    custom_error_css = """
        <style>
        .custom-error-box {
            background-color: white;  /* Light red background */
            border-left: 6px solid red;  /* Red left border for the error */
            padding: 8px;
            border-radius: 5px;
            color: red;
        }
        .custom-error-box p {
            font-weight: bold;
            margin: 10;
            font-size: 18px;
        }
        .custom-error-box span {
            color: black;  /* Regular text color */
            font-weight: normal;
        }
        </style>
        """

    # FUNCTION TO RENDER CUSTOM ERROR WITH CSS
    def custom_error_message(message):
        # Apply the custom CSS globally
        st.markdown(custom_error_css, unsafe_allow_html=True)

        # Render the error message with the custom styling
        st.markdown(
            f"""
                <div class="custom-error-box">
                    <p>🚨 Error: <span>{message}</span></p>
                </div>
                """,
            unsafe_allow_html=True
        )


    # VALIDATE DESTINATION IT'S REAL WORLD OR NOT.
    def destination_validate():
        prompt = f"""
        Validate if the given destination '{destination}' is a real-world location (Town, City, State, or Country).
        1. If the destination is anything else (e.g., cafe, museum, garden, or random characters like abc, gvsadjv, jkvnk, etc.), return the following JSON format:
            {{
                "error": "Your destination should be a Town, City, State, or Country."
            }}
        2. If the destination is valid, simply return the following JSON format.
            {{
                "valid": "Your destination is correct."
            }}
        **Make sure to return only the message as a JSON object if the destination is invalid. I don't want any additional information.**
        ** Give only Error message as json format. i don't want any extra information's.
        """
        validated_responses = google_llm_model(prompt)
        # print(f"__________val_________\n{validated_responses}")

        return validated_responses


# ==================================== JSON_Format, Generate, Delete, ADD =================================================================

    # CREATE FUNCTION TO GET DATA AS JSON FORMAT
    def js_frmt():
        prompt = f"""
         The response should be in the following JSON format:
        {{
          "days": [
            {{
              "day": 1,
              "activities": [
                {{
                  "title": "New or existing activity title",
                    "description": "Description of the activity",
                    "transportation": "Transportation details",
                    "travel_tips": "Tips for the activity",
                    "link": "https://www.google.com/maps/search/?api=1&query=Activity+Name+at+Location+Name" ,  "Please provide a dynamic Google Maps link for the following activity and location. The link should direct to the specific location on Google Maps. Use the format: https://www.google.com/maps/search/?api=1&query=Activity+Name+at+Location+Name.For example, if the activity is 'Eiffel Tower' and the location is 'Paris', the link should be: https://www.google.com/maps/search/?api=1&query=Eiffel+Tower+at+Paris.,
                    "approx_cost": "Cost details" # i don't want '₹' symbol here you should use currency name of {destination}. don't use ₹ symbol any where.
                    "visiting_time": "New time slot",
                }}
                # More activities...
              ]
            }}
            # More days...
          ]
        }}

        make sure all the activity of each day it should be unique

        """
        return prompt


    # FUNCTION CALL TO GET DATA AS JSON FORMAT
    json_format_prompt = js_frmt()


    # CREATE FUNCTION TO GENERATE NEW ITINERARY USING LLM MODEL FUNCTION CALL
    def generate_itinerary(destination, day, travel_type):
        # CONSTRUCT THE PROMPT FOR THE LLM MODEL
        prompt = f"""Hey AI Trip Planner, schedule my dream trip as per the given details! I want to explore {destination} for {day} days. I'm planning a {travel_type} trip. Please provide me with a detailed itinerary, including rest times, ensuring the destination is exist in real world.

        **Strictly follow this Instructions:**            
        1. **Ensure that the itinerary you generate is specifically tailored to a {travel_type} trip. If there are not enough suitable places to visit for this type of trip, avoid suggesting destinations that do not align with the travel purpose. 

        The itinerary should include:
        * A precise daily schedule from 9 O'clock in the morning to 10 O'clock at night. If any activity starts earlier than 9 O'clock in the morning, schedule the itinerary accordingly. Ensure that each and every minute of my itinerary is planned.
        * Must-see attractions with estimated time spent at each, including opening hours, entry fees, and proper Google Maps link for each attraction. The link should be accessible by clicking on the title of the attraction.
        * make sure don't use currency symbol in Itinerary. You can use Currency name instead of symbol.
        * Popular top-rated restaurants near each attraction for breakfast, lunch, and dinner, with their approximate timings or cuisine types, also make sure these activity should be at it's relevant time like so arrange it like breakfast should be before 10:30 Am, lunch should be 12 to 2 Pm, or dinner should be 8 to 9 PM.
        * Make sure suggest restaurant that is nearby the previous activity if you suggest 
        * Also give correct or dynamic google map link which is clickable or redirect able to google map for all activities
        * Recommendations for the best modes of transport to get around the location.
        * Helpful suggestions for maximizing my trip, including local customs, must-try snacks, and hidden gems.
        * Unique titles for each rest time in the itinerary to ensure no repetitive activities across different days.
        * Ensure that all activities for each day are unique and not repeated on other days.  
        * Make sure If you have not any perfect and accurate data for each and every activity's budget breakdown then don't give wrong or assumed data, if you have latest and perfect budget data then only give budget for that activity.
        * Don't give me specific activity for rest time. i don't want it, give me only that activities which are relevant to the trip.
        * Show the image of that place as per the activity title 

        {json_format_prompt}
        
        """

        # print(type(json_format_prompt))
        # print(json_format_prompt)
        try:
            response = groq_llm_model(prompt)
            return response
        except BadRequestError as e:
            custom_error_message(f" retry... ")
            print(f"BadRequestError___________\n\n {e}")
        except Exception as e:
            custom_error_message(f"Enter a valid & real world destination. system error is {e}")


    # DELETE ACTIVITY FROM CURRENT ITINERARY AND RE SCHEDULE TIME
    def delete_activity(activity_title, day):
        itinerary = st.session_state.itinerary

        # CONVERT ITINERARY TO A FORMATTED JSON STRING
        dump_data = json.dumps(itinerary, indent=2)

        # CONSTRUCT THE PROMPT FOR THE LLM MODEL
        prompt = f"""
        You are an AI trip planner. I need to delete the activity "{activity_title}" in day {day} from the following itinerary and reschedule the remaining activities timing accordingly. Here is the current itinerary in JSON format:

        ** Exisitng itinerary: **
        {dump_data} \n

        Please remove the specified activity and adjust timing for the remaining activities accordingly. time should be adjusted after delete activity. 
        - Adjust time according activity Don't assign too much time if we can explore that place in less time or also adjust eating(breakfast, lunch, dinner) time maximum 1 hour, you can give more then 1 hours. if the restaurant is little far from currant activity location.
        - Make sure don't try to add same activity in place of deleted activity that is already present in ** Exisitng itinerary: ** that is above given and prefer that new activity according {travel_type} trip, it should be suitable to {travel_type} trip.
        - you can add similar activity in place of deleted activity, if it's possible.
        - Update proper time according activity don't give too much time for that activity if it's not taken much time to explore or complete it like we can complete dinner in max 1 hour then give time according it.
        Provide the updated itinerary in the same JSON format:

        {json_format_prompt}
        """

        try:
            reschedule_itinerary = groq_llm_model(prompt)

            # CHECK IF THE RESPONSE IS VALID JSON AND HANDLE ACCORDINGLY
            reschedule_itinerary_json = json.loads(reschedule_itinerary)

            # UPDATE SESSION STATE WITH THE NEW ITINERARY
            st.session_state.itinerary = reschedule_itinerary_json
            return reschedule_itinerary
        except BadRequestError as e:
            custom_error_message(f"Error: {activity_title} might be already deleted or it's present .")
            print(f"BadRequestError___________\n\n {e}")
        except Exception as e:
            custom_error_message(f"Ensure the activity title is valid. System error: {e}")


    # CREATE FUNCTION TO ADD NEW ACTIVITY IN ITINERARY AND REGENERATE IT USING LLM MODEL FUNCTION CALL
    def add_activity(js_data, day_index, new_activity, destination):


        currant_itinerary = {json.dumps(js_data, indent=2)}

        # CONSTRUCT THE PROMPT FOR THE LLM MODEL
        prompt = f"""

        **Currant Itinerary**
        {currant_itinerary}
        \n \n 
        
        - Hey Ai Trip Planner, I want to add {new_activity} place or activity in day {day_index + 1} to your given data {currant_itinerary}. 
        - Make sure I want the same data format so add that {new_activity} in the itinerary and adjust the time according to the all activities of the {day_index + 1}. 
        - If {new_activity} already in currant itinerary then Generate below error only. Don't Generate anything else.
            -{{
                "error": "{new_activity} already in current itinerary."
            }}
        - Please provide a correct and accurate response. 
        
        {json_format_prompt}
        
        """

        try:
            activity_added = groq_llm_model(prompt)
            return activity_added
        except BadRequestError as e:
            # custom_error_message(f"BadRequestError_________\n\n{e}")
            custom_error_message(f"{new_activity} already in current itinerary if not then retry...")
            print(f"BadRequestError___________\n\n {e}")
        except Exception as e:
            custom_error_message(f"Enter a valid activity in the real world. system error is {e}")


# =========================================== Button ==========================================================


    with st.container():
        # BUTTON TO GENERATE ITINERARY
        if st.button('Get Plan'):
            with st.spinner("Scheduling..."):
                if travel_type is None or destination == "":
                    custom_error_message("Please fill out all required fields.")
                elif "error" not in destination_validate().lower():
                    # CALLING GENERATE ITINERARY FUNCTION AND GET RESPONSE DATA FROM LLM
                    data = generate_itinerary(destination, day, travel_type)

                    if data:
                        if "₹" in data:
                            datas = data.replace("₹", "RS.")
                            print("₹ symbole is replaced____________________________\n\n")
                            js_data = json.loads(datas)
                            # STORE JS_DATA AS SESSION STATE ITINERARY
                            st.session_state.itinerary = js_data
                        else:
                            print(f"data--------------------->{data}\n\n")
                            js_data = json.loads(data)
                            # STORE JS_DATA AS SESSION STATE ITINERARY
                            st.session_state.itinerary = js_data
                else:
                    custom_error_message("Your Destination should be Town, City, State or Country.")


# =========================================== Display itinerary ==========================================================


    # DISPLAY AND MODIFY ITINERARY
    if 'itinerary' in st.session_state:
        js_data = st.session_state.itinerary

        # logging.info(f"Full Itinerary: {js_data}")  # Log full itinerary for debugging

        errors = str(js_data)

        if not "ERROR" in errors.upper():
            # GENERATE AND DISPLAY THE PDF DOWNLOAD BUTTON
            pdf_data = json_to_pdf(st.session_state.itinerary, day, destination, travel_type)

            # if len(pdf_data) >= 1000:
            if st.download_button(label="Download as PDF", data=pdf_data.encode('latin-1'),
                                  file_name=f"{destination} - Itinerary.pdf", mime="application/pdf"):
                st.success("PDF successfully downloaded.")

            # Display each day and activities
            if isinstance(js_data, dict) and 'days' in js_data and isinstance(js_data['days'], list):

                image_url = get_wikipedia_image_for_specific_destination(destination)

                # Add the image URL to the activity data, or set a default if not found
                js_data["image"] = image_url if image_url else "default_image_url"
                st.image(js_data["image"])
                st.write("ok main")

                # Add "image" key with a URL from Wikipedia for each activity
                for day in js_data["days"]:
                    for activity in day["activities"]:
                        # Fetch the image URL using the activity title
                        title_query = activity["title"]
                        image_url = get_wikipedia_image_for_specific_destination(title_query)

                        # Add the image URL to the activity data, or set a default if not found
                        activity["image"] = image_url if image_url else "default_image_url"

                # destination_image = get_wikipedia_image_for_specific_destination(destination)
                # # destination_image = download_from_pexels("goa", per_page=5)
                # print(f"\n___________{destination_image}\n")

                # if "None" not in destination_image or destination_image is not None:
                #     st.image(destination_image)

                for day_index, day in enumerate(js_data['days']):
                    st.header(f":material/clear_day: Day {day_index + 1}")

                    # ADD "Add Activity" BUTTON TO ADD NEW ACTIVITY
                    with st.expander(f"Add Activity to Day {day_index + 1}"):
                        new_activity = st.text_input(f"Activity Title for Day {day_index + 1}",
                                                     key=f"title_{day_index}")

                        if 'itinerary' in st.session_state:
                            if st.button(f"Add Activity to Day {day_index + 1}", key=f"add_{day_index}"):
                                with st.spinner("Adding..."):
                                    # DISPLAY DATA ON STREAMLIT
                                    if new_activity:
                                        items = [item for item in day.get("activities", [])]
                                        activity_list = [item['title'].lower() for item in items]
                                        new_activity = new_activity.lower()

                                        if new_activity not in activity_list:
                                            # CALLING A ADD ACTIVITY FUNCTION TO ADD ACTIVITY
                                            Added_itinerary = add_activity(js_data, day_index, new_activity,
                                                                           destination)
                                            if Added_itinerary:
                                                # UPDATE SESSION STATE WITH ADDING NEW ACTIVITY
                                                st.session_state.itinerary = json.loads(Added_itinerary)
                                                st.write("Activity added. Updating itinerary...")
                                                st.rerun()
                                        else:
                                            custom_error_message(
                                                "Please add an unique activity, your entered activity already in the list.")
                                    else:
                                        custom_error_message("Please fill in all the fields to add an activity.")


                    # Display each activity
                    for activity_index, activity in enumerate(day.get("activities", [])):
                        with st.container():
                            col1, col2 = st.columns([1, 0.2])
                            # logging.info(f"activity {activity_index}: ------------------------> {activity}\n")
                            with col1:
                                with st.expander(
                                        f":blue[{activity.get('visiting_time')}] \n \n :material/location_on: {activity.get('title')} \n \n {activity.get('description')}"):

                                    for key, value in activity.items():
                                        if key == "link" and value != "":
                                            st.markdown(f":material/my_location: Location: {activity['link']}")

                                        if key == "transportation" and value != "":
                                            st.markdown(
                                                f":material/departure_board: Transportation: {activity['transportation']}")

                                        if key == "travel_tips" and value != "":
                                            st.markdown(
                                                f":material/featured_play_list: Travel Tips: {activity['travel_tips']}")


                                    exclude_keys = {"title","visiting_time","description" }

                                    # Check if all values (excluding specified keys) are empty
                                    all_empty = all(
                                        not value for key, value in activity.items() if key not in exclude_keys)

                                    # Display the result
                                    if all_empty:
                                        st.markdown("")



                                    with col2:
                                        col1, col2 = st.columns((1,1))
                                        with col1:
                                            # activity_image_name = activity.get('title')
                                            # destination_image = get_wikipedia_image_for_specific_destination(f"{activity_image_name}, {destination}")
                                            # print(f"______{activity_image_name}___________====> {destination_image} \n")
                                            # # destination_image = download_from_pexels(activity_image_name, per_page=5)


                                            if activity['image'] is not None and "Error" not in activity['image']:
                                                try:
                                                    st.image(activity['image'], width=100)
                                                    st.write("ok")
                                                except Exception as e:
                                                    print(f"No image or error occurred.{e}")

                                        with col2:
                                            delete_button = st.button(f'Delete ',
                                                                      key=f"delete_Day{day_index}_{activity_index}_{activity['title']}")

                                # Handle delete button click
                                if delete_button:
                                    with st.spinner("Deleting..."):
                                        deleted_itinerary = delete_activity(activity['title'],day=day_index+1)
                                        st.write("Activity deleted. The itinerary has been updated.")

                                        if deleted_itinerary:
                                            st.session_state.itinerary = json.loads(deleted_itinerary)
                                            st.rerun()
                                        break

                    if day_index > 1:
                        st.divider()

                    flag = True

        else:
            custom_error_message("Your destination should be a Town, City, State or Country")


# ============================================ CSS =========================================================


    page_bg_img = f"""
    <style>

    [data-testid="stHeader"] {{
        background: rgba(255,255,255,0);
        height:50px;
        padding : 40px 0px;
        color:black;
    }}

    [data-testid="stApp"]{{
        background-image: url('data:image/png;base64,{bg_image_base64}');
        background-size: cover; /* or 'contain' based on your needs */
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: local;
    }}

    [data-testid=stSidebarCollapsedControl] img{{
        width : 220px;
        height : 35px;
    }}

    [data-testid="stAppViewBlockContainer"] {{
        backdrop-filter: {"blur(7px)" if flag == False else "blur(-25px)"};  /* Apply blur effect to the background */
        background: {"rgba(255, 255, 255, 0.28)" if flag == False else "linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,1))"};  /* Light semi-transparent background */
        border-radius: 20px;  /* Rounded corners */
        padding: 20px ;
        width:  100%;
        max-width: {"900px" if flag == False else "95vw"};
        box-shadow: 0px 4px 30px rgba(0, 0, 0, 0.1);  /* Subtle shadow effect */
        margin-top : 3%;
    }}
    .st-emotion-cache-1jicfl2{{
        backdrop-filter: {"blur(7px)" if flag == False else "blur(-25px)"};  /* Apply blur effect to the background */
        background: {"rgba(255, 255, 255, 0.28)" if flag == False else "linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,1))"};  /* Light semi-transparent background */
        border-radius: 20px;  /* Rounded corners */
        padding: 20px ;
        width:  100%;
        max-width: {"900px" if flag == False else "95vw"};
        box-shadow: 0px 4px 30px rgba(0, 0, 0, 0.1);  /* Subtle shadow effect */
        margin-top : 3%;
    }}
    [data-testid="stMarkdownContainer"] [data-testid="stHeadingWithActionElements"] h2 [data-testid="stHeaderActionElements"]{{
        display : none;
    }}
    input[type="text"] {{
            autocomplete: off;
    }}
    #ai-trip-itinerary span{{
        display : none;
    }}
    button{{
    }}
    button:hover {{
        border-color : black !important;
        background-color : black !important;
        color : white !important;
        font-weight : bold;
    }}
    .st-emotion-cache-ocqkz7 .st-emotion-cache-1h8evva div div div div div button{{
        width : 99% !important;
    }}
    .st-emotion-cache-bm2z3a{{
        height : {flag == False and "100vh"};
        display : {flag == False and "flex"};
        justify-content: {flag == False and "center"};
        margin-top : {flag == True and "4%"};   
    }}
    .st-emotion-cache-p5msec:hover svg{{
        fill :orange;
    }}
    [data-baseweb="input"] [data-baseweb="base-input"] input {{
        background-color: {flag == True and "lightgray !important"};
    }}
    [data-baseweb="select"] .st-at {{
        background-color: {flag == True and "lightgray"};
    }}
    .st-emotion-cache-1vt4y43{{
        color:{"white" if flag == False else "black !important"};
        background-color : {"orange" if flag == False else "white !important"};;
        width : {"100%" if flag == False else "20% !important "};
        margin-top:2%;
        padding:10px;
        border-color:{"orange" if flag == False else "black !important"};;
        font-weight : bold;
    }}
    .st-emotion-cache-1vt4y43:active{{
        color:{"white" if flag == False else "black !important"};
        background-color : {"orange" if flag == False else "white !important"};;
        width : {"100%" if flag == False else "20% !important"};
        margin-top:2%;
        padding:10px;
        border-color:{"orange" if flag == False else "black !important"};;
        font-weight : bold;
    }}
    .st-emotion-cache-1qw6le8{{
        border-color: rgb(255, 165, 0) rgba(250, 250, 250, 0.2) rgba(250, 250, 250, 0.2);
    }}
    .st-emotion-cache-1rsyhoq p{{
        font-size : 18px;
        margin-left :10px !important ;
        font-weight : 600;
    }}
    .st-emotion-cache-jkfxgf:hover {{
        color : black !important;
    }}
    .st-emotion-cache-1dtefog:hover {{
        color:black !important;
    }}
    .st-emotion-cache-p5msec:hover{{
        color : black !important;
    }}
    .st-emotion-cache-jkfxgf p{{
        font-size : 16px;
    }}
    .st-emotion-cache-1rsyhoq p{{
        margin : 0px;
    }}
    label [data-testid="stMarkdownContainer"] {{
        color : black;
    }}
    label {{
        font-size : 20px;
    }}
    [data-testid="stHeaderActionElements"]  {{
        display : none;
    }}
    @media (max-width: 768px) {{

        [data-testid="stApp"] {{
            background-position: center;
        }}

        [data-testid=stSidebarCollapsedControl] img {{
            width: 130px;
            height: 20px;
            margin-top:5%;
        }}

        [data-testid="stHeader"] {{
            background: rgba(255,255,255,0.7);
            height : 70px;
            padding : 10px 0px;
            color:black;
        }}

        .st-emotion-cache-1vt4y43 {{
            width: 100%;
        }}

        .st-emotion-cache-bm2z3a{{
            padding : 10px !important;
        }}
        [data-testid="stAppViewBlockContainer"] {{
            height : none;
            margin-top : 20%;
        }}
    }}

    div[data-testid="stToolbar"] {{
        visibility: hidden;
        height: 50%;
        position: fixed;
    }}
    div[data-testid="stDecoration"] {{
        visibility: hidden;
        height: 0%;
        position: fixed;
    }}
    div[data-testid="stStatusWidget"] {{
        visibility: hidden;
        height: 50%;
        position: fixed;
    }}
    #MainMenu {{
        visibility: hidden;
        height: 0%;
    }}
    header {{
        visibility: hidden;
        height: 0%;
    }}
    footer {{
        visibility: hidden;
        height: 0%;
    }}
    .stTextInput  .st-d7{{
        border-bottom-color : orange 
    }}
    .stTextInput  .st-d6{{
        border-top-color : orange 
    }}
    .stTextInput  .st-d5{{
        border-right-color : orange 
    }}
    .stTextInput  .st-d4{{
        border-left-color : orange 
    }}
    # Travel input
    .st-emotion-cache-1ooc4wg  .st-d6{{
        border-top-color : orange !important;
    }}
    .st-emotion-cache-1ooc4wg  .st-d5{{
        border-right-color : orange !important;
    }}
    .st-emotion-cache-1ooc4wg  .st-d4{{
        border-left-color : orange !important;
    }}
    # Day increment descrement button
    .st-emotion-cache-zbmw0q:focus:enabled {{
        background : black;
        color : white;
    }}
    # budget
    .st-emotion-cache-6v4t1a.focused {{
        border-color : orange;
    }}
    # Button
    .st-emotion-cache-1vt4y43:focus-visible{{
        box-shadow : orange 0px 0px 0px 0.2rem
    }}
    .st-emotion-cache-1vt4y43:focus:not(:active){{
        border-color : {"orange" if flag == False else "black"};
        color : {"white" if flag == False else "black"};
    }}
    # input field   
    [data-baseweb="input"].st-dl{{
        border-bottom-color : orange !important;
    }}
    [data-baseweb="input"].st-dk{{
        border-top-color : orange !important;
    }}
    [data-baseweb="input"].st-dj{{
        border-right-color : orange !important;
    }}
    [data-baseweb="input"].st-di{{
        border-left-color : orange !important;
    }}
    .stSelectbox div .st-d7{{
        border-bottom-color : orange !important;
    }}
    .stSelectbox div .st-d6{{
        border-top-color : orange !important;
    }}
    .stSelectbox div .st-d5{{
        border-right-color : orange !important;
    }}
    .stSelectbox div .st-d4{{
        border-left-color : orange !important;
    }}
    .st-emotion-cache-6v4t1a.focused{{
        border-color : orange;
    }}
    .st-emotion-cache-zbmw0q:focus:enabled{{
        background-color : black;
    }}


    </style>
    """

    # # SET BACKGROUND IMAGE
    st.markdown(page_bg_img, unsafe_allow_html=True)

