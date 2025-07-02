from faker import Faker
from pythainlp.transliterate import romanize

fake = Faker('th_TH')

# for i in range(500):
#     full_name_th = fake.name_male()
#     name_parts = full_name_th.strip().split()
#     print(name_parts)
#     name_en = romanize(name_parts[0]).capitalize()
#     name_en = romanize(name_parts[0], engine="thai2rom")
#     print(name_en)

# name_en = romanize("ภูวฤณ")
# print(name_en)

name = "ผลบุญ"
romanized = romanize(name, engine="thai2rom")
print(romanized)