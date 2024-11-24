import streamlit as st
import requests
from Tripgenie import tripgenie
from streamlit_js_eval import get_page_location
from dotenv import load_dotenv
import os


# Function to determine if the user is logged in
def is_user_logged_in():
    return 'access_token' in st.session_state and st.session_state.access_token is not None


# Function to set the layout dynamically
def set_dynamic_page_layout():
    # Conditionally set layout based on login status and popup
    if is_user_logged_in() and st.session_state.get('popup_shown', False):
        layout_choice = "wide"
    else:
        layout_choice = "centered"

    # Set page configuration dynamically
    favicon_path = "images/Yellow_Favicon.png"
    st.set_page_config(page_title="TripGenie AI", page_icon=favicon_path, layout=layout_choice, menu_items=None, )


# Call page layout setting at the beginning
set_dynamic_page_layout()

logo_path = "images/Inexture_logo_2023.png"
st.logo(logo_path, icon_image=logo_path, link="https://www.inexture.com/")

load_dotenv()


def login(username, password, project_url):
    url = os.getenv('SERVER_LOGIN_URL')
    data = {"username": username, "password": password, "project_url": project_url}
    response = requests.post(url, data=data)
    return response.json(), response.status_code


def get_current_page_url():
    page_location = get_page_location()
    return page_location.get('origin', 'URL not found') if page_location else None



def handle_login():
    with st.container():
        col1, col2 = st.columns([0.4, 0.6])

        with col1:
            st.image(logo_path, width=220)
            st.markdown("<h2>Login to TripGenie AI</h2>", unsafe_allow_html=True)

            with st.form(key='login_form', border=False):
                username = st.text_input("Email Address", placeholder="Enter your email")
                password = st.text_input("Password", placeholder="Enter your password", type="password")
                project_url = get_current_page_url()
                submit_button = st.form_submit_button(label='Login')

            if submit_button:
                if username and password and project_url:  # Check if all fields are filled
                    response_data, status_code = login(username, password, project_url)
                    if status_code == 200:
                        st.session_state.access_token = response_data['tokens']['access']
                        st.session_state.first_login = True  # Set first login flag
                        st.success("Login successful!")
                        st.session_state.page = 'welcome'  # Redirect to welcome popup after login
                        st.rerun()  # Rerun the app to update the state
                        return True
                    elif status_code == 401:
                        st.error("You do not have permission to access this URL")
                    else:
                        st.error("Invalid email or password")
                else:
                    st.error("Please enter both email and password")

        with col2:
            dummy_image = "images/Top_Banner.png"
            st.image(dummy_image)

    return False




def show_welcome_popup():
    # Create a container for the white box
    with st.container(border=True):
        st.markdown("""
                            <div style="padding: 20px; ">
                            <h2 style="text-align: center;">Welcome to TripGenie!</h2>

                            <p style = "font-weight : bold; font-size : 18px; text-align : center;">TripGenie is your AI-powered travel companion, creating personalized Trip plans tailored to your preferences.</p>

                            <h2>How to Use:</h2>
                            <ol>
                                <li style= "font-size : 18px;"><b style = "font-weight : bold;">Enter Your Details:</b> Number of days, Destination, Travel type</li>
                                <li style= "font-size : 18px;"><b style = "font-weight : bold;">Generate Trip Plan:</b> Click "Get Plan" to receive your customized Trip Plan</li>
                                <li style= "font-size : 18px;"><b style = "font-weight : bold;">Customize Your Plan:</b> Remove activities you don't like, add new activities of your choice, and watch as TripGenie adjusts your schedule in real-time</li>
                                <li style= "font-size : 18px;"><b style = "font-weight : bold;">Download and Explore:</b> Get your final Trip Plan as a PDF with interactive Google Maps links to explore your destinations</li>
                            </ol>

                            <p style = "font-weight : bold;">Start planning your dream trip with TripGenie today!</p>
                            </div>
                        """, unsafe_allow_html=True)

    # Add some vertical space
    st.write("")
    st.write("")

    # Center the "Got it!" button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Got it!"):
            st.session_state.popup_shown = True
            st.rerun()


# print(show_welcome_popup())
def main():
    isWelcomePopAvailable = False
    isLogin = False

    if 'first_login' not in st.session_state:
        st.session_state.first_login = False
    if 'popup_shown' not in st.session_state:
        st.session_state.popup_shown = False
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None

    if st.session_state.access_token is None:
        isLogin = True
        handle_login()
    else:
        if st.session_state.first_login and not st.session_state.popup_shown:
            isWelcomePopAvailable, isLogin = True, False
            show_welcome_popup()
        else:
            isWelcomePopAvailable = True
            tripgenie()

    print(isWelcomePopAvailable)

    st.markdown(f"""
        <style>

            .st-emotion-cache-1shnq3u{{
                gap : {"0px" if isLogin == True else ""};
            }}
            .st-emotion-cache-1kyxreq{{
                margin-top : {"8px" if isLogin == True else ""};
            }}


            .stApp{{
                overflow-y : hidden;
            }}
            [data-testid="stSidebarCollapsedControl"] a img{{  
                width : 220px;     
                height : 35px;

            }}

            .st-emotion-cache-13ln4jf{{
                height : {"100%" if isWelcomePopAvailable == True else ""};
                display : flex;
                justify-content : center;
                align-items : center;
                padding : {"0px" if isLogin == True else "6rem 3rem 4rem"};
                max-width: {"unset" if isWelcomePopAvailable == False else ""};
                display:{"block" if isWelcomePopAvailable == False else ""};
            }}
            .st-emotion-cache-1biyfi2{{    
                width : {"740px" if isLogin == False else "unset"};          
            }}
            .stButton button {{
                width :{"100%"};
                background-color : orange;
                color : white;
                padding :10px;
            }}
            .stButton button:hover {{
                width : 100%;
                background-color : orange;
                border-color : orange;  
                color : white;
                padding :10px;
            }}
            .stButton button:focus:not(:active){{
                border-color : orange;
                color : white;
            }}
            .stFormSubmitButton button {{
                width :{"100%"};
                background-color : orange;
                color : white;
                padding :10px;
                margin-top : 10px;
            }}
            .stFormSubmitButton button:hover {{
                width : 100%;
                background-color : orange;
                border-color : orange;  
                color : white;
                padding :10px;
            }}
            .stFormSubmitButton button:focus:not(:active){{
                    border-color : orange;
                    color : white;
            }}
            label [data-testid="stMarkdownContainer"] p{{
                font-size : 16px;
            }}
            .st-emotion-cache-4uzi61{{
                padding : {"5%" if isWelcomePopAvailable == True else ""};
                border : 1px solid gray;
                border-radius : 5%;
                box-shadow : 10px 10px 10px gray;
            }}
            .st-cc {{
                border-bottom-color : orange;
            }}
            .st-cb {{
                border-top-color : orange;
            }}
            .st-ca {{
                border-right-color : orange;
            }}
            .st-c9 {{
                border-left-color : orange;
            }}
            [data-testid="stHeaderActionElements"]{{
                display : none;
            }}
            [data-testid="stToolbar"]{{
                display : none;
            }}

            .st-emotion-cache-1bzkvni, .st-emotion-cache-1yycg8b{{
                align-items: center;
                padding: 80px;
                display : flex;
                box-sizing: border-box;
                justify-content:center;
            }}
            .st-emotion-cache-1yycg8b [data-testid="stVerticalBlockBorderWrapper"]{{
                width:100%;
                max-width:550px;
            }}
            .st-emotion-cache-12fmjuu{{
                background : transparent;
            }}

            .st-emotion-cache-1cn4dee{{
                gap : 2rem;
            }}
            .st-emotion-cache-1dp5vir{{
                display : none;
            }}
             @media (max-width: 768px) {{
                .st-emotion-cache-fplge5 {{
                    display: none;
                }}

                .st-emotion-cache-1bzkvni, .st-emotion-cache-1yycg8b{{
                    padding : 0px;
                }}
                .st-emotion-cache-1v0mbdj{{
                    display : none; 
                }}
                 .st-emotion-cache-13ln4jf{{
                    height : 100%;
                    padding : {"4rem 1rem 4rem" if isWelcomePopAvailable == True else "6rem 1rem 4rem"};
                    max-width : none;
                    display : {"flex" if isLogin ==True else "block"};
                 }}
                .stMain div div {{
                    width : {"100%" if isLogin == True else ""};
                }}
                .st-emotion-cache-4uzi61{{ 
                    padding : 0px;
                    border : none;
                    border-radius : none;
                    box-shadow : none;
                }}
                [data-testid=stSidebarCollapsedControl] img {{
                    width : 160px;
                    height : 35px;
                }}

            }}


            /* Adjust columns for better spacing on mobile and tablet */
            @media (min-width: 1024px) {{
                [data-testid="stSidebarCollapsedControl"] a img{{ 
                    display :{"" if isWelcomePopAvailable == True else "none"};
                }}
            }}

            [data-testid="StyledFullScreenButton"] {{
                display : none;
            }}

        </style>

    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()