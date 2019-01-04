print ("Memulai")
from collections import Counter
import pandas as pd
import requests
import json
import re


#------------------ CONFIGURATION -------------------------------
dict_filename = "lib2.csv"
input_filename = "convo.csv"


#load convo
convo = pd.read_csv(input_filename)

#nama kolom di "dict_filename"
head_keywords = 'keywords'
head_interest = 'interest'

#nama baris di "input_filename"
head_userid = 'userid'
head_username = 'username'
head_caption = 'caption'
head_postid = 'postid'
head_likes_count = 'like_count'
head_comment_count = 'comment_count'



#------------------ OUTPUT FILE -------------------------------
#1. tb_convo_count_percent.csv
#2. tb_pivot_percent.csv
#3. tb_user_statistics.csv
#4. tb_user_keywords.txt


#------------------	FUNCTION DEFINITIONS ------------------------

#Untuk pembeda crawller kak Fidao sama Pak Maman
"""user_ff = False
if 'following' in convo.columns:
	user_ff = True
if user_ff == True:"""
	
#Untuk ambil jumlah followers dan following di instagram
def insta(user_name):
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	ff = []
	situs = 'https://www.instagram.com/' + user_name + '/'
	try: 
		response = requests.get(url=situs, headers=headers)
	except: 
		print ("Koneksi Internet Error!" + " Username: " + user_name + " Gagal diproses!")
	try:
		json_match = re.search(r'window\._sharedData = (.*);</script>', response.text)
		profile_json = json.loads(json_match.group(1))['entry_data']['ProfilePage'][0]['graphql']['user']


		follower_temp = profile_json['edge_followed_by']['count']
		following_temp = profile_json['edge_follow']['count']
		status_username = True #User ditemukan
	except:
		follower_temp = "-"
		following_temp = "-"
		status_username = False #User tidak ada

	ff.append(follower_temp)
	ff.append(following_temp)
	ff.append(status_username) 
	ff.append(user_name)
	return ff

def hitung_persen(nilai, total):
	try:
		x =  nilai / total
	except:
		x = 0
	return x

def delete_petik(word):
	word_x = word
	if type(word) != int:
		word_x = word.replace('"','').replace("'","")
	return word_x


#------------------ DATA LOADING --------------------------------


#load dictionary dari file CSV yang bernama lib2.csv
mydict = {}
dfdict = pd.read_csv(dict_filename)
list_interest =  []
for index, row in dfdict.iterrows():
	keyword = str(row[head_keywords]).replace('"','').replace(",", "").replace("/"," ").replace("("," ").replace(")","").lower()
	interst = str(row[head_interest]).lower()
	

	mydict[keyword] = interst
	list_interest.append(interst)
list_interest = list(set(list_interest))
str_interest = ""
str_sumof_interest = ""

#List jumlah interest (dapat menyesuaikan, sesuai lib2.csv)
for i in list_interest:
	str_interest = str_interest + "," + i
	str_sumof_interest = str_sumof_interest + "," + "Sum of " + i 



#Seting Output1
output_name = "tb_convo_count_percent.csv"
f = open(output_name, "w", encoding="utf-8")
label = "Username,Convo" + str_interest + "\n"
f.write(label)

#Seting Output2
output_name2 = "tb_pivot_percent.csv"
g = open(output_name2, "w")
label2 = "Username" + str_sumof_interest + "\n"
g.write(label2)

#Seting Output3
output_name3 = "tb_user_statistics.csv"
h = open(output_name3, "w")
label3 = "Username,Total Post,Total Likes,Average Like,Total Comment,Average Comment,Engagement,Followers,Following\n"
h.write(label3)

#Seting Output4
output_name4 = "tb_user_keywords.txt"
z = open(output_name4, "w")
label4 = "Username,PostID,Caption,Keyword,Interest\n"
z.write(label4)



hit = 1
hit_user = 1

#Data merupakan sebuah kumpulan kata secara temporary pada setiap caption (BERSIFAT TEMPORARY)
data = []


#perhitungan tiap post
post = []

#perhitungan untuk semua post
user_post = {}

#data user list
user_list = []


#Pencatatan. Hasilnya nantinya akan | count_user_posts['username'] = jumlah post |
count_user_posts = {}
count_user_likes = {}
count_user_comments = {}
count_user_followers = {}
count_user_following = {}






for index, row in convo.iterrows():
	user_id = delete_petik(row[head_userid])
	username = row[head_username]
	caption = str(row[head_caption]).replace(",","").replace(r"\u","|").replace("\n","|").replace("\r","|").lower().strip()
	post_id = delete_petik(row[head_postid])

	print (str(hit) + ". " + username + ": " + caption)
	hit += 1
	if username not in user_list:
		user_list.append(username)


	#Mengecek apakah username sudah masuk di dalam count_user_post
	if username not in count_user_posts:
		count_user_posts[username] = 1
	else: 
		count_user_posts[username] += 1

	if username not in count_user_likes:
		count_user_likes[username] = row[head_likes_count]
	else:
		count_user_likes[username] += row[head_likes_count]

	if username not in count_user_comments:
		count_user_comments[username] = row[head_comment_count]
	else:
		count_user_comments[username] += row[head_comment_count]

	#Untuk mencocokan keyword dalam caption
	for i in mydict:
		if i in caption:
			post.append(mydict[i])
			#menulis CSV tentang keyword yang cocok dengan convo/caption yang kena
			isi = (username + ',-' + str(post_id) + ',' + str(caption) + "," + str(i) + "," + str(mydict[i]))
			if type(isi) != bytes:
				isi = isi.encode('utf-8')

			isi = str(isi).replace("b'","").replace("'","") + "\n"
			isi = isi.replace("-",'"')
			z.write(isi)

	#Sebagai counter. atau perhitungan jumlah berapa interest nya (travel, berapa culinary, berapa musik, dll)
	counter = Counter(post)
	post = []
	total_keyword = sum(counter.values())
	

	#Mengambil nilai dari setiap interestnya, dan menyimpannya dalam satu data list
	nilai_interets = {}
	str_nilai_interest = ""
	for i in list_interest:
		nilai_interets[i] = hitung_persen(counter[i], total_keyword)
		str_nilai_interest = str_nilai_interest + "," + str(nilai_interets[i])


		#Header = "username,convo, interest..."
	line = username + "," + caption + str_nilai_interest + "\n"
	f.write(line)

	if username not in user_post:
		user_post[username] = {}

	#menghitung jumlah interest dari masing2 user (semua post)
	for i in list_interest:
		if str(i) not in user_post[username]:
			user_post[username][i] = 0
		user_post[username][i] += nilai_interets[i]


print (" ")
print ("Profiling...")
print (" ")
for i in user_list:

	#i = username

	str_nilai_interest_user = ""
	for j in user_post[i]:
		 str_nilai_interest_user = str_nilai_interest_user + "," + str(user_post[i][j])


	#total_percent = user_post[i]['traveling'] + user_post[i]['fashion'] + user_post[i]['culinary'] + user_post[i]['music']
	total_percent = sum(user_post[i].values())
	str_percent_total = ""
	percent_total = {}
	for j in list_interest:
		percent_total[j] = hitung_persen(user_post[i][j], total_percent)
		str_percent_total = str_percent_total + "," + str(percent_total[j])

	#Header = "Username,Sum of interest"
	g.write(str(i) + str_percent_total + "\n")

	average_likes = count_user_likes[i] / count_user_posts[i]
	average_comments = count_user_comments[i] / count_user_posts[i]

	engagement = average_likes + average_comments


	if i not in count_user_followers:
		count_user_followers[i] = insta(i)[0]
	if i not in count_user_following:
		count_user_following[i] = insta(i)[1]


	#Header = "Username,Total Post,Total Likes,Average Like,Total Comment,Average Comment,Engagement,Followers,Following\n"
	h.write(str(i) + "," + str(count_user_posts[i]).replace(",","|") + "," + str(count_user_likes[i]).replace(",","|") + "," + str(average_likes).replace(",","|") + "," + str(count_user_comments[i]).replace(",","|") + "," + str(average_comments).replace(",","|") + "," + str(engagement) + "," + str(count_user_followers[i]).replace(",","|") + "," + str(count_user_following[i]).replace(",","|") + "\n")
	print (str(hit_user) + ". Username: " + i  + " Followers: " + str(count_user_followers[i]) + ". Following: " + str(count_user_following[i]) + ".")
	hit_user += 1
f.close()
g.close()
h.close()
z.close()
print("Data Tersimpan")
print("Proses Selesai")
