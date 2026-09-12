import json
import pandas as pd
import pypdf
import requests
import streamlit as st

st.set_page_config(
    page_title="Talous-AI & Vaurastumisassistentti", page_icon="📈", layout="centered"
)

# --- TURVALLISUUS: HAETAAN API-AVAIN PALVELIMELTA TAI SIVUPALKIN KENTÄSTÄ ---
try:
    default_api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    default_api_key = ""

st.title("📈 Talous-AI & Vaurastumisassistentti (Free & Pro)")
st.write(
    "Älykäs talousassistentti arkeen ja sijoittamiseen. "
    "Käytä ilmaisia perustoimintoja tai päivitä Pro-versioon!"
)

# --- SIVUPALKKI: TILAUS & PRO-AKTIVOINTI ---
st.sidebar.header("💎 Käyttöoikeus & Tilaukset")

if "is_pro" not in st.session_state:
    st.session_state.is_pro = False

# Pakotetaan expander aina auki (expanded=True), jotta avaimen syöttökenttä näkyy varmasti
with st.sidebar.expander("🔑 OpenAI API-asetukset", expanded=True):
    st.markdown("Syötä OpenAI:n API-avain tekoälytoimintoja varten.")
    user_api_input = st.text_input("OpenAI API-avain", value="", type="password", key="user_openai_key")
    
    # Tarkistetaan avain suoraan ja tallennetaan session_stateen, ettei se katoa
    if user_api_input:
        st.session_state.active_api_key = user_api_input.strip()
    elif "active_api_key" not in st.session_state:
        st.session_state.active_api_key = default_api_key

api_key = st.session_state.get("active_api_key", "")

# Näytetään pieni merkkivalo sivupalkissa kertomaan onko avain syötetty
if api_key:
    st.sidebar.success("✅ API-avain tallennettu muistiin!")
else:
    st.sidebar.error("❌ Ei API-avainta syötetty.")

st.sidebar.markdown("---")

if st.session_state.is_pro:
    st.sidebar.success("✅ Pro-tila aktivoituna tässä istunnossa!")
    if st.sidebar.button("Kirjaudu ulos Pro-tilasta"):
        st.session_state.is_pro = False
        st.rerun()
else:
    st.sidebar.info("Olet **Ilmaisversiossa**.")
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Päivitä Pro-versioon")
    st.sidebar.markdown(
        "Hanki kaikki tekoälyominaisuudet, PDF-palkkalaskelman luku, kuvaskanneri ja älykäs hintavertailu!"
    )
    st.sidebar.markdown("**Hinnat:**")
    st.sidebar.markdown("- 🌟 **4,90 € / kk**")
    st.sidebar.markdown("- 🔥 **49,00 € / vuosi** *(säästä 17%)*")
    
    with st.sidebar.expander("🔑 Minulla on jo aktivointikoodi", expanded=True):
        entered_code = st.text_input("Syötä lisenssikoodi / PIN", value="", type="password", key="entered_pin")
        if st.button("Aktivoi Pro"):
            if entered_code.strip() == "salasana123": 
                st.session_state.is_pro = True
                st.success("Pro aktivoitu onnistuneesti!")
                st.rerun()
            else:
                st.error("Virheellinen koodi. Kokeile salasana123")

    st.sidebar.markdown("---")
    st.sidebar.markdown("💡 *Haluatko ostaa Pro-oikeuden? Ota yhteys ylläpitäjään.*")

is_pro_unlocked = st.session_state.is_pro

# Apufunktio OpenAI-kutsuille requests-kirjaston kautta
def call_openai_api(key, prompt_text, model="gpt-3.5-turbo"):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt_text}]
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
    if response.status_code == 200:
        res_json = response.json()
        return res_json["choices"][0]["message"]["content"]
    else:
        raise Exception(f"API-virhe ({response.status_code}): {response.text}")

# Pääsovelluksen välilehdet
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📝 Tulot & Menot", 
        "🎯 Sijoituspuskuri", 
        "💡 Smart Budget", 
        "🏷️ Omat Hinnat",
        "🛒 Perusruokabudjetti",
        "🍳 Pro: Ruokalista & Hintavertailu"
    ]
)

if "custom_products" not in st.session_state:
    st.session_state.custom_products = pd.DataFrame(
        [
            {"Poista": False, "Tuote / Pakkaus": "Kanafilee (400g)", "Kauppa": "Prisma", "Hinta (€)": 4.50},
            {"Poista": False, "Tuote / Pakkaus": "Maito (1l)", "Kauppa": "S-Market", "Hinta (€)": 1.19},
            {"Poista": False, "Tuote / Pakkaus": "Raejuusto (400g)", "Kauppa": "Prisma", "Hinta (€)": 2.15},
            {"Poista": False, "Tuote / Pakkaus": "Banaanit (niput)", "Kauppa": "Lidl", "Hinta (€)": 2.50},
            {"Poista": False, "Tuote / Pakkaus": "Riisi (1kg)", "Kauppa": "K-Citymarket", "Hinta (€)": 1.60},
        ]
    )

# --- TAB 1: TULOT & MENOT ---
with tab1:
    st.subheader("1. Tulot & Manuaaliset menot")
    
    if is_pro_unlocked:
        st.markdown("### 📄 [PRO] Tuo tulotiedot suoraan PDF-palkkalaskelmasta")
        uploaded_pdf = st.file_uploader("Lataa palkkalaskelma (PDF)", type=["pdf"], key="pdf_uploader_main")
        
        if uploaded_pdf is not None:
            if not api_key:
                st.error("⚠️ Syötä OpenAI API-avain sivupalkin asetuksiin ennen tiedoston lukemista.")
            else:
                try:
                    reader = pypdf.PdfReader(uploaded_pdf)
                    pdf_text = ""
                    for page in reader.pages:
                        pdf_text += page.extract_text() or ""
                    
                    with st.spinner("Tekoäly lukee palkkatietoja PDF:stä..."):
                        prompt = (
                            "Etsi seuraavasta palkkalaskelman tekstistä NETTO-palkka (käteen jäävä summa) "
                            "sekä BRUTTO-palkka. Palauta tulos muodossa: Netto: [numero], Brutto: [numero].\n\n"
                            f"Teksti:\n{pdf_text[:3000]}"
                        )
                        result_text = call_openai_api(api_key, prompt)
                        st.info(f"AI:n löytämät tiedot tekstistä: {result_text}")
                except Exception as err:
                    st.error(f"Virhe tiedoston käsittelyssä: {err}")
    else:
        st.info("🔒 **PDF-palkkalaskelman automaattinen luku** vaatii Pro-version (4,90 €/kk).")

    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input("Netto-kuukausitulot (€)", min_value=0.0, value=2500.0, step=50.0)
        vuokra = st.number_input("Vuokra / Asuntolaina (€)", min_value=0.0, value=800.0, step=50.0)
        sahko = st.number_input("Sähkö (€)", min_value=0.0, value=40.0, step=10.0)
        vesi = st.number_input("Vesi (€)", min_value=0.0, value=20.0, step=5.0)
    with col2:
        ruokakulut = st.number_input("Arvioidut ruokakulut (kauppa) (€)", min_value=0.0, value=350.0, step=25.0)
        suoratoisto = st.number_input("Suoratoistopalvelut (€)", min_value=0.0, value=45.0, step=5.0)
        muut_menot = st.number_input("Muut pakolliset kulut (€)", min_value=0.0, value=150.0, step=25.0)

    total_expenses = vuokra + sahko + vesi + ruokakulut + suoratoisto + muut_menot
    net_left = monthly_income - total_expenses
    st.info(f"📊 Yhteenveto: Tulot {monthly_income} € | Menot **{total_expenses} €** | Jäljelle jää: **{net_left} €**")

# --- TAB 2: SIJOITUSPUSKURI ---
with tab2:
    st.subheader("2. Sijoittamiskeskeinen optimointi & Korkoa korolle -laskuri")
    current_balance = st.number_input("Tilillä oleva nykyinen käyttöraha yhteensä (€)", value=3500.0, key="curr_bal")
    buffer_need = st.number_input("Turvapuskurin tavoite (€)", value=2000.0, key="buff_need")

    if st.button("Laske sijoitettava ylijäämä"):
        excess_cash = current_balance - buffer_need
        if excess_cash > 0:
            st.success(f"💡 **Sijoituspotentiaali:** Noin **{excess_cash:.0f} euroa** puskurin ylittävää rahaa.")
        else:
            st.info("Keskity ensin saavuttamaan turvapuskuritavoite.")

    st.markdown("---")
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        alkup_sijoitus = st.number_input("Alkusijoitus (€)", value=1000.0, step=100.0)
        kk_sijoitus = st.number_input("Kuukausisäästö (€)", value=150.0, step=25.0)
    with col_inv2:
        sijoitus_aika_vuotta = st.slider("Sijoitusaika (vuotta)", 1, 40, 10)
        arvioitu_tuotto_prosentti = st.slider("Arvioitu vuosituotto (%)", 0.0, 20.0, 7.0, 0.5)

    kokonaissumma = alkup_sijoitus
    kuukausi_tuotto = arvioitu_tuotto_prosentti / 100 / 12
    for _ in range(sijoitus_aika_vuotta * 12):
        kokonaissumma = (kokonaissumma + kk_sijoitus) * (1 + kuukausi_tuotto)
    
    st.info(f"📊 **Salkun arvo {sijoitus_aika_vuotta} v. jälkeen:** **{kokonaissumma:,.0f} €**")

    if is_pro_unlocked:
        st.markdown("### 🤖 [PRO] Kriittinen tekoälyanalyysi sijoitussuunnitelmasta")
        sijoitus_kohde_kuvaus = st.text_area("Strategia:", "Sijoitan globaaliin indeksirahastoon.")
        if st.button("Pyydä Pro AI-analyysi"):
            if api_key:
                try:
                    result_text = call_openai_api(api_key, f"Analysoi kriittisesti sijoitusstrategiaa: {sijoitus_kohde_kuvaus}")
                    st.markdown(result_text)
                except Exception as err:
                    st.error(f"Virhe tekoälypyynnössä: {err}")
            else:
                st.error("⚠️ Syötä OpenAI API-avain sivupalkin asetuksiin.")
    else:
        st.markdown("*(🔒 Pro-käyttäjät saavat tähän tekoälyn tarkan riskianalyysin).*")

# --- TAB 3: SMART BUDGET ---
with tab3:
    st.subheader("3. Smart Budget & Viikkoseuranta")
    weekly_food_target = st.number_input("Viikoittainen ruokabudjetti (€)", value=80.0)
    actual_food_spent = st.number_input("Tällä viikolla käytetty (€)", value=65.0)
    
    if is_pro_unlocked:
        if st.button("Hae Pro-palaute viikon kulutuksesta"):
            if api_key:
                try:
                    result_text = call_openai_api(api_key, f"Arvioi viikkobudjettia (tavoite {weekly_food_target}, toteutunut {actual_food_spent}) huumorilla.")
                    st.markdown(result_text)
                except Exception as err:
                    st.error(f"Virhe tekoälypyynnössä: {err}")
            else:
                st.error("⚠️ Syötä OpenAI API-avain sivupalkin asetuksiin.")
    else:
        st.info("🔒 AI-palaute budjetille vaatii Pro-tilan.")

# --- TAB 4: HINNAT & KUITTISKANNERI ---
with tab4:
    st.subheader("🏷️ Omat tuotehinnat & Kuvaskanneri")
    
    if is_pro_unlocked:
        st.markdown("### 📸 [PRO] Älykäs Kuvaskanneri")
        uploaded_files = st.file_uploader("Lataa kuitteja", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        if uploaded_files:
            st.success(f"Ladattu {len(uploaded_files)} kuvaa skannattavaksi.")
    else:
        st.info("🔒 Kuittien automaattinen tekoälyskanneri on Pro-ominaisuus.")

    st.markdown("### 📋 Omat tallennetut hinnat")
    edited_df = st.data_editor(st.session_state.custom_products, num_rows="dynamic", key="product_editor")
    if "Poista" in edited_df.columns:
        st.session_state.custom_products = edited_df[edited_df["Poista"] == False].reset_index(drop=True)

# --- TAB 5: PERUSRUOKABUDJETOIJA ---
with tab5:
    st.subheader("🛒 Arjen Perusruokabudjetti & Älykkäät Säästövinkit")
    st.write("Tarkista suositellut ruokabudjetit ja nappaa parhaat arjen säästökikat käyttöön!")

    family_size_basic = st.selectbox("Valitse talouden koko", ["1 henkilö", "2 henkilöä", "Perhe (3-4 hlö)"], key="t5_family")
    
    if family_size_basic == "1 henkilö":
        suf_suositus = "200 – 260 € / kk (~50–65 € / vko)"
        kerta_ostos = "Noin 40–50 € / kauppareissu"
    elif family_size_basic == "2 henkilöä":
        suf_suositus = "350 – 450 € / kk (~90–110 € / vko)"
        kerta_ostos = "Noin 70–90 € / kauppareissu"
    else:
        suf_suositus = "600 – 800 € / kk (~150–200 € / vko)"
        kerta_ostos = "Noin 120–160 € / kauppareissu"

    st.info(f"📊 **Suositeltu ruokabudjetti:** {suf_suositus} | Suositeltava kertaostos: {kerta_ostos}")

    st.markdown("---")
    st.markdown("### 💡 Parhaat ilmaiset säästövinkit ruokakauppaan")
    
    col_vinkki1, col_vinkki2 = st.columns(2)
    with col_vinkki1:
        st.markdown("#### 1. Suunnitelmallisuus & Kauppalista")
        st.write(
            "- **Käy kaupassa vain kerran tai kahdesti viikossa:** "
            "Jatkuva heräteostoksilla käynti kasvattaa ruokamenoja.\n"
            "- **Älä koskaan mene kauppaan nälkäisenä:** "
            "Nälkäisenä ostoskoriin tarttuu helposti kalliita tuotteita."
        )
        st.markdown("#### 2. Tuotemerkit & Hinnoittelu")
        st.write(
            "- **Suosi kauppojen omia merkkejä** (esim. Rainbow, K-Menu, Pirkka): "
            "Tuotteet ovat usein samaa laatua.\n"
            "- **Tarkista kilohinta:** Älä tuijota pelkkää pakkaushintaa."
        )
    with col_vinkki2:
        st.markdown("#### 3. Hävikkiruoka & Sesongit")
        st.write(
            "- **Hyödynnä laputetut tuotteet:** "
            "Etsi -30% ja -60% punalappuiset tuotteet.\n"
            "- **Syö sesongin mukaan:** "
            "Juurekset ja kaalit ovat edullisimmillaan."
        )
        st.markdown("#### 4. Ruoanlaitto & Pakastaminen")
        st.write(
            "- **Tee kerralla isompi satsi:** "
            "Padat ja laatikkoruoat riittävät useammalle aterialle.\n"
            "- **Hyödynnä pakastinta:** "
            "Jaa ylijäämäruoka annosrasioihin."
        )

# --- TAB 6: PRO - RUOKALISTA & HINTAVERTAILU ---
with tab6:
    st.subheader("🍳 [PRO] Tarkka ruokalista, mittojen optimointi & Kauppojen hintavertailu")
    
    if is_pro_unlocked:
        col_a, col_b = st.columns(2)
        with col_a:
            diet_choice = st.selectbox("Valitse ruokavalio", ["Sekasyöjä", "Kasvissyöjä", "Vegaani", "Gluteeniton", "Laktoositon"], key="t6_diet")
            days_count = st.slider("Ajanjakso (päivää)", min_value=1, max_value=7, value=7, key="t6_days")
            body_weight = st.number_input("Paino (kg, vapaaehtoinen)", min_value=30.0, max_value=250.0, value=75.0, step=0.5, key="t6_weight")
            body_height = st.number_input("Pituus (cm, vapaaehtoinen)", min_value=120, max_value=230, value=175, step=1, key="t6_height")
        with col_b:
            goal_choice = st.selectbox(
                "Tavoite", 
                [
                    "Terveellinen perusruokavalio",
                    "Laihdutus / Painonhallinta (Kalorivaje)", 
                    "Lean Bulk (Lihasmassan kasvu)",
                    "Lean Cut (Kiristely)",
                    "Tarjousten hyödyntaminen / Halvin"
                ],
                key="t6_goal"
            )
            meals_per_day = st.slider("Aterioita / päivä", min_value=1, max_value=6, value=3, key="t6_meals")

        family_size_pro = st.selectbox("Talouden koko (kenelle ruuat mitoitetaan)", ["1 henkilö", "2 henkilöä", "Perhe (3-4 hlö)", "Suurperhe (5+ hlö)"], key="t6_family")

        allergies_input = st.text_input("Allergiat / Vältettävät aineet", value="", key="t6_allergies")
        stores_to_compare = st.multiselect("Valitse kaupat vertailuun", ["Lidl", "S-Market", "Prisma", "K-Market", "K-Citymarket"], default=["Lidl", "Prisma", "S-Market"], key="t6_stores")

        if st.button("Generoi Pro-ruokalista ja hintavertailutaulukko"):
            if not api_key:
                st.error("⚠️ Syötä OpenAI API-avain sivupalkin asetuksiin ennen tekoälypyyntöä.")
            elif len(stores_to_compare) < 1:
                st.warning("Valitse vähintään yksi kauppa.")
            else:
                stores_str = ", ".join(stores_to_compare)
                prompt = (
                    f"Suunnittele erittäin tarkka {days_count} päivän ruokalista taloudelle, jonka koko on '{family_size_pro}': "
                    f"ruokavalio {diet_choice}, tavoite {goal_choice}, ateriat {meals_per_day} kpl/pvä, "
                    f"käyttäjän paino {body_weight} kg ja pituus {body_height} cm (käytä näitä mittoja arvioidaksesi optimaalisen kalorien ja makroravinteiden tarpeen), "
                    f"allergiat: '{allergies_input}'. Kirjoita vastaus suomeksi.\n\n"
                    f"VAATIMUKSET VASTAUKSELLE:\n"
                    f"1. **Vaihtuvat ateriat**: Jokaisella päivällä (Päivä 1 - Päivä {days_count}) TÄYTYY OLLA ERI AIKAAN ERI ATERIAT. Älä toista samaa ruokalistaa sellaisenaan eri päiville, vaan luo monipuolinen ja vaihteleva viikko-ohjelma.\n"
                    f"2. **Ruokalista ja hinnat**: Näytä jokaiselle päivälle omat ateriat, arvioidut kalorit/makrot painon/pituuden perusteella sekä tarkasti hinta per ateria sekä hinta per päivä.\n"
                    f"3. **Täydellinen ostoslista**: Listaa KAIKKI ruokalistassa käytettävät raaka-aineet ja elintarvikkeet, jotka tarvitaan viikon ruokien valmistukseen. Huomioi ostoslistassa todelliset myyntipakkaukset (esim. 400g kanafilee, 1kg riisi, 1l maito) eikä pelkkiä reseptimittoja.\n"
                    f"4. **Kattava hintavertailutaulukko**: Tee Markdown-taulukko, jossa on sarakkeina: [Tuote / Pakkaus, Tarvittava määrä viikolle, {stores_str}]. **Varmista, että jokaiselle tuotteelle löytyy hinta jokaiseen valittuun kauppaan ({stores_str})**, eikä kenttiä jätetä tyhjäksi.\n"
                    f"5. **Yhteenveto**: Laske taulukon loppuun rivit: **Keskimääräinen hinta per päivä**, **Keskimääräinen hinta per ateria** sekä **YHTEENSA (€) koko viikon ostoksille** vierekkäin jokaiselle vertailukaupalle."
                )
                with st.spinner("Luodaan optimoitua Pro-ruokalistaa ja hintavertailua..."):
                    try:
                        result_text = call_openai_api(api_key, prompt)
                        st.markdown(result_text)
                    except Exception as err:
                        st.error(f"Virhe tekoälypyynnössä: {err}")
    else:
        st.warning("🔒 **Tämä välilehti on lukittu Pro-käyttäjille (4,90 €/kk).** Päivitä Pro-versioon sivupalkin kautta avataksesi edistyneen ruokalistageneraattorin ja hintavertailun!")
