from neo4j import GraphDatabase, basic_auth
import pandas as pd
import random
from faker import Faker
from tqdm import tqdm
from ast import literal_eval


### Make Test Data

def get_test_data():
    fake = Faker('ko_KR')
    genders = ['M', 'F']
    test_list = []
    for i in range(len(df)):
        for idx, gender in enumerate(genders):
            name = fake.name()
            age = random.randrange(20, 55)
            data = f"{name},{age},{gender}"
            test_list.append(data)

    return test_list

# alphabet_samles 변수에 저장된 문자열의 문자와 숫자들 중 임의로 뽑아
# length의 길이만큼의 영어 숫자 조합 문자열을 생성
def random_id(length):
    result = ""
    alphabet_samples = "abcdefghizklmnopqrstuvwxyz1234567890"  # id 생성에 사용할 글자들을 정의
    for i in range(length):
        result += random.choice(alphabet_samples)
    return result

def random_restaurant(df):
    result = []
    for i in range(5):
        result.append(random.choice(df['rest_name']))
    return result

def get_test_csv(df):
    names = []
    ids = []
    ages = []
    genders = []
    visited_rest = []

    for i in range(len(df)):
        name = get_test_data()[i][0:3]
        age = get_test_data()[i][4:6]
        gender = get_test_data()[i][7:]
        user_id = random_id(6)
        rests = random.choice(df['rest_name'])

        names.append(name)
        ages.append(age)
        genders.append(gender)
        ids.append(user_id)
        visited_rest.append(rests)

    test_df = pd.DataFrame(
        {
            'user_name': names,
            'user_id': ids,
            'age': ages,
            'gender': genders,
            'visited_rest': visited_rest
        }
    )

    test_df.to_csv('./test_user.csv', index=False)
    csv_file = pd.read_csv('test_user.csv')

    return csv_file



class Node():
    def add_person(tx, name, user_id, age, gender, visited_rest):
        tx.run("MERGE (person:Person {name:$name,  user_id:$user_id, age:$age, gender:$gender, visited_rest:$visited_rest})",
            name=name, user_id=user_id, age=int(age), gender=gender, visited_rest=visited_rest)


    def add_restaurant(tx, rest_name, cuisine):
        tx.run("MERGE (r:Restaurant {rest_name:$rest_name, cuisine:$cuisine})",
               rest_name=rest_name, cuisine=cuisine)


    def add_review(tx, rest_name, reviewer, rating, review, date):   ### add user_id
        tx.run("MERGE (b:Review {rest_name: $rest_name, reviewer:$reviewer, rating:$rating, review: $review, date:$date})",
               rest_name=rest_name, reviewer=reviewer, rating=rating, review=review, date=date)

    def add_blog_review(tx, rest_name, blog_link):
        tx.run("MERGE (blog:Blog_review { rest_name:$rest_name, blog_link:$blog_link})",
               rest_name=rest_name, blog_link=blog_link)


    def add_menu(tx, rest_name, menus, price,cuisine):
        tx.run("MERGE (c:Menu {rest_name: $rest_name, menus: $menus, price:$price, cuisine: $cuisine})",
               rest_name=rest_name, menus=menus, price=price, cuisine=cuisine)


    def add_cuisine(tx, rest_name, cuisine):
        tx.run("MERGE (cuisine:Cuisine {rest_name:$rest_name, cuisine: $cuisine})",
               rest_name=rest_name, cuisine=cuisine)


    def add_address(tx, rest_name, city, district, address, website, phone):
        tx.run("MERGE (d:Address {rest_name:$rest_name, city:$city, district:$district, address: $address, website:$website, phone:$phone})",
               rest_name=rest_name, city=city, address=address, district=district, website=website, phone=phone)


    def add_city(tx, city):
        tx.run("MERGE (c:City {city:$city })",
               city=city)

    def add_district(tx, city, district):
        tx.run ("MERGE (d:District {city:$city, district:$district})",
                city=city, district=district)


    def add_facilities(tx, rest_name, facilities, tag):
        tx.run("MERGE (fa:Facilities { rest_name:$rest_name, facilities:$facilities, tag:$tag})",
               rest_name=rest_name, facilities=facilities, tag=tag)


    def add_service(tx, rest_name, service_quality, service_detail, open_close):
        tx.run("MERGE (s:Service {rest_name:$rest_name, service_qualiy:$service_quality, service_detail:$service_detail, open_close:$open_close})",
               rest_name=rest_name, service_quality=service_quality, service_detail=service_detail, open_close=open_close)


    def add_weather(tx, weather, tag):
        tx.run("MERGE (w:Weather { weather:$weather, tag:$tag})",
               weather=weather, tag=tag)


    def add_tag(tx, rest_name, cuisine, tag, facilities):
        tx.run("MERGE (t:Tag {rest_name:$rest_name, cuisine:$cuisine, tag:$tag,  facilities:$facilities})",
               rest_name=rest_name, cuisine=cuisine, tag=tag, facilities=facilities)



class Relation():


    def has_restaurant(tx):
        tx.run("MATCH (c:Cuisine),(r:Restaurant)"
               "WHERE (c.rest_name)=(r.rest_name)"
               "MERGE (c)-[:HAS_RESTAURANT]->(r)"
               )

    def has_cuisine(tx):
        tx.run("MATCH (c:Cuisine),(r:Restaurant)"
               "WHERE (c.rest_name)=(r.rest_name)"
               "MERGE (r)-[:HAS_CUISINE]->(c)"
               )

    def has_address(tx):
        tx.run("MATCH (r:Restaurant),(a:Address)"
               "WHERE (r.rest_name)=(a.rest_name)"
               "MERGE (r)-[:HAS_ADDRESS]->(a)"
               )


    def has_review(tx):
        tx.run("MATCH (r:Restaurant),(b:Review)"
               "WHERE (b.rest_name)=(r.rest_name)"
               "MERGE (r)-[:HAS_REVIEW]->(b)"
               )

    def has_blog_review(tx):
        tx.run("MATCH (r:Restaurant),(blog:Blog_review)"
               "WHERE (r.rest_name)=(blog.rest_name)"
               "MERGE (r)-[:HAS_REVIEW]->(blog)"
               )


    def located_in(tx):
        tx.run("MATCH (d:District),(a:Address),(c:City)"
               "WHERE (c.city)=(d.city)"
               "AND (a.district)=(d.district)"
               "MERGE (a)-[:LOCATED_IN]->(d)-[:LOCATED_IN]->(c);"
               )


    def has_menu(tx):
        tx.run("MATCH (a:Restaurant),(m:Menu)"
               "WHERE (a.rest_name)=(m.rest_name)"
               "MERGE (a)-[r:HAS_MENU]->(m)")


    def is_customer(tx):
        tx.run("MATCH (p:Person),(r:Restaurant)"
               "WHERE (p.visited_rest)=(r.rest_name)"
               "MERGE (p)-[:IS_CUSTOMER]->(r)"
               )

    def has_customer(tx):
        tx.run("MATCH (p:Person),(r:Restaurant)"
               "WHERE (p.visited_rest)=(r.rest_name)"
               "MERGE (r)-[:HAS_CUSTOMER]->(p)"
               )

    def has_facility(tx):
        tx.run("match (r:Restaurant),(f:Facilities)"
               "where (r.rest_name)=(f.rest_name)"
               "merge (r)-[:HAS_FACILITY]->(f)"
               )

    def has_tag(tx):
        tx.run("match (r:Restaurant),(t:Tag)"
               "where (r.rest_name)=(t.rest_name)"
               "merge (r)-[:HAS_TAG]->(t)")

# Neo4j -> Gephi 에서 parsing error의 원인이 될 수 있음
# def clean_text_for_neo4j(row):
#     text = row['title_c']
#     text = re.sub(pattern='[^a-zA-Z0-9ㄱ-ㅣ가-힣]', repl='', string=text)
#     # print("영어, 숫자, 한글만 포함 : ", text )
#     return text


### Connect with Neo4j
# Neo4j 브라우저에서 설정한 계정의 ID, PASSWORD를 통해 접속
try:
    # greeter = GraphDatabase.driver("bolt://localhost:11003", auth=("neo4j", "0701"))
    uri = "bolt://127.0.0.1:7687"
    greeter = GraphDatabase.driver(uri, auth=("neo4j", "0724"))
    print('Connected')
except:
    print('Connect Failed')


### neo4j로 전달할 데이터
df = pd.read_csv('/home/haewon/바탕화면/Crawler_복제본/ERCLab Crawler/data/gimcheon_0916.csv') # 음식점

# df = pd.read_csv('/home/haewon/바탕화면/Crawler_복제본/ERCLab Crawler/data/touristSpot.csv') # 관광명소
test_df = get_test_csv(df)




### 노드와 관계 생성, 데이터 주입
with greeter.session() as session:

    for idx in tqdm(range(len(df))):

        """ make nodes """
        # session.write_transaction(Node.add_person,
        #                           name=test_df.iloc[idx]['user_name'],
        #                           user_id=test_df.iloc[idx]['user_id'],
        #                           age=test_df.iloc[idx]['age'],
        #                           gender=test_df.iloc[idx]['gender'],
        #                           visited_rest=test_df.iloc[idx]['visited_rest'])

        session.write_transaction(Node.add_restaurant,
                                  rest_name=df.iloc[idx]['rest_name'],
                                  cuisine=df.iloc[idx]['cuisine'])

        session.write_transaction(Node.add_cuisine,
                                  rest_name=df.iloc[idx]['rest_name'],
                                  cuisine=df.iloc[idx]['cuisine'])

        session.write_transaction(Node.add_address,
                                  rest_name=df.iloc[idx]['rest_name'],
                                  city="경상북도 김천시",
                                  district=df.iloc[idx]['address'][9:12],
                                  address=df.iloc[idx]['address'],
                                  website=df.iloc[idx]['website'],
                                  phone=df.iloc[idx]['url'])

        session.write_transaction(Node.add_city,
                                  city="경상북도 김천시")

        session.write_transaction(Node.add_district,
                                  city="경상북도 김천시",
                                  district=df.iloc[idx]['address'][9:12] # 음식점
                                  # district=df.iloc[idx]['address'][7:10] # 관광명소
                                  )

        '''Facilities'''
        try:
            facilities = literal_eval(df['facilities'][idx])
        except:
            facilities = []

        for x in range(len(facilities)):
            session.write_transaction(Node.add_facilities,
                                      rest_name=df.iloc[idx]['rest_name'],
                                      facilities=facilities[x],
                                      tag=df.iloc[idx]['tags']
                                      )

        '''Tags'''
        tags = literal_eval(df['tags'][idx])
        for j in range(len(tags)):

            session.write_transaction(Node.add_tag,
                                      rest_name=df.iloc[idx]['rest_name'],
                                      tag=tags[j],
                                      cuisine=df.iloc[idx]['cuisine'],
                                      facilities=df.iloc[idx]['facilities'])



        """ 메뉴 & 리뷰 딕셔너리에서 추출   """

        menu = literal_eval(df['menus'][idx])
        for j in range(len(menu)):
            try:
                session.write_transaction(Node.add_menu,
                                          rest_name=df.iloc[idx]['rest_name'],
                                          menus=menu[j]['title'],
                                          price=int(menu[j]['price'].replace(',','')),
                                          cuisine=df.iloc[idx]['cuisine'])
            except: # '변동가격' or '무료' 처리
                session.write_transaction(Node.add_menu,
                                          rest_name=df.iloc[idx]['rest_name'],
                                          menus=menu[j]['title'],
                                          price=menu[j]['price'],
                                          cuisine=df.iloc[idx]['cuisine'])


        review = literal_eval(df['reviews'][idx])
        for j in range(len(review)):
            session.write_transaction(Node.add_review,
                                      rest_name=df.iloc[idx]['rest_name'],
                                      reviewer = review[j]['reviewer'],
                                      rating = review[j]['rating'],
                                      review=review[j]['review'],
                                      date=review[j]['review_date'])


        blog_review = literal_eval(df['blog_reviews'][idx])
        for j in range(len(blog_review)):
            session.write_transaction(Node.add_blog_review,
                                      rest_name=df.iloc[idx]['rest_name'],
                                      blog_link=blog_review[j]['link'])






        """ make relations """
        try:
            session.write_transaction(Relation.has_menu)
            session.write_transaction(Relation.has_review)
            session.write_transaction(Relation.has_blog_review)
            session.write_transaction(Relation.is_customer)
            session.write_transaction(Relation.located_in)
            session.write_transaction(Relation.has_restaurant)
            session.write_transaction(Relation.has_address)
            session.write_transaction(Relation.has_cuisine)
            session.write_transaction(Relation.has_customer)
            session.write_transaction(Relation.has_facility)
            session.write_transaction(Relation.has_tag)
        except EOFError:
            print('rest_name : ', Node.add_address['rest_name'])
            pass

    print("Done! :-)")





