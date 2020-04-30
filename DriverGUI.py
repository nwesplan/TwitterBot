import sys

import matplotlib
from PyQt5 import QtSql
import pandas as pd
from GUI_UI import *
import pyodbc
from PyQt5.QtWidgets import QDialog, QApplication
import keys as k
from textblob import TextBlob
from nltk.corpus import stopwords
from operator import itemgetter
import matplotlib.pyplot as plt
import folium


cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+k.server+';DATABASE='+k.database+';UID='+k.username+';PWD='+ k.password)
cursor = cnxn.cursor()
DATABASE_TABLELIST_QUERY ="""SELECT TABLE_NAME FROM TWEETS.INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"""

class MyForm(QDialog):
    def __init__(self):
        #initialize setup
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Python-Microsoft SQL Server Visual Database Management Studio")

        #set clickbox variables to false
        self.barchart = False
        self.geomap = False
        self.sentiment_analysis = False

        #disable search button until user selects the table name
        self.ui.searchTextButton.setEnabled(False)

        #initialize stop word button and stop words
        self.ui.add_stop_word_button.clicked.connect(self.addStopWord)
        self.stop_words = stopwords.words('english')

        #create combobox dropdown menus
        self.buildComboBoxes()


        #intiialize button click events
        self.ui.getTableButton.clicked.connect(self.getTableName)
        self.ui.searchTextButton.clicked.connect(self.getSearchText)
        self.ui.refresh_table_button.clicked.connect(self.refreshTableList)
        

        #intiialize calendar - not used
        self.ui.calendarWidget.clicked.connect(self.showDate)

        #intialize clickbox events
        self.ui.checkbox_bar.stateChanged.connect(self.clickbox_bar)
        self.ui.checkbox_geo.stateChanged.connect(self.clickbox_geo)
        self.ui.checkBox_sentiment.stateChanged.connect(self.clickbox_sentiment)

        #intiialize horizontal slider and set values
        self.ui.horizontal_slider.setMinimum(20)
        self.ui.horizontal_slider.setMaximum(100)
        self.ui.horizontal_slider.setValue(20)
        self.horizontal_slider_value = self.ui.horizontal_slider.value()
        self.ui.slider_label.setText(str(self.ui.horizontal_slider.value()))
        self.ui.horizontal_slider.valueChanged.connect(self.changeValue)

        stylesheet = """
            
            
            
            QCheckBox::indicator:unchecked {
                border: 1px solid silver;
                background-color: darkred;
            }
            QCheckBox::indicator:checked {
                border: 1px solid silver;
                background-color: #3F3;
            }
            
            
                    
                """
        self.setStyleSheet(stylesheet)

        self.show()

    #refreshes list of tables combo box
    def refreshTableList(self):
        #execute table list query
        cursor.execute(DATABASE_TABLELIST_QUERY)
        results = cursor.fetchall()
        rlist = []
        #omit tables with OLD and USER_LOCATIONS,
        #old tables will mostly work but cause errors with hashtags and mentions
        for x in range(len(results)):
            if 'OLD' not in results[x][0] and 'USER_LOCATIONS' not in results[x][0]:
                print('results:', results[x][0])
                rlist.append(results[x][0])
        #clear current list and add new list, disable search box
        self.ui.comboBox.clear()
        self.ui.comboBox.addItems(rlist)
        self.ui.searchTextButton.setEnabled(False)

    #add stop words
    def addStopWord(self):
        self.stop_words.append(self.ui.stop_words_input.text())
        self.ui.stopwords_label.setText("Added stop word: "+ self.ui.stop_words_input.text())

    #creates all the combo box lists
    def buildComboBoxes(self):
        cursor.execute(DATABASE_TABLELIST_QUERY)
        results = cursor.fetchall()
        rlist = []
		#omit tables with OLD and USER_LOCATIONS,
        #old tables will mostly work but cause errors with hashtags and mentions
        for x in range(len(results)):
            if 'OLD' not in results[x][0] and 'USER_LOCATIONS' not in results[x][0]:
                print('results:', results[x][0])
                rlist.append(results[x][0])
		#hashtag mention text list
        hmtlist = []
        hmtlist.append('text')
        hmtlist.append('hashtags')
        hmtlist.append('mentions')
		#device list
        devicelist = []
        devicelist.append('any device')
        devicelist.append('IPHONE')
        devicelist.append('ANDROID')
        devicelist.append('WEBAPP')
        devicelist.append('IPAD')
        devicelist.append('WEBCLIENT')
        devicelist.append('TWEETDECK')
        devicelist.append('TWEETCASTER')
        devicelist.append('MOBILEWEB')

        self.ui.text_hashtag_combo.addItems(hmtlist)
        self.ui.device_used_combo.addItems(devicelist)
        self.ui.comboBox.addItems(rlist)

        self.text_combo_box = self.ui.text_hashtag_combo.currentText()
        self.device_used = self.ui.device_used_combo.currentText()
        

    #change horizontal slider value and set set label
    def changeValue(self):
        self.horizontal_slider_value = self.ui.horizontal_slider.value()
        self.ui.slider_label.setText(str(self.horizontal_slider_value))

    #methods for handling clickboxes, bar chart, sentiment chart, and geo map
    def clickbox_sentiment(self, state):
        if state == QtCore.Qt.Checked:
            self.sentiment_analysis = True
        else:
            self.sentiment_analysis = False

    def clickbox_bar(self, state):
        if state == QtCore.Qt.Checked:
            self.barchart = True
        else:
            self.barchart = False
        
    def clickbox_geo(self, state):
        if state == QtCore.Qt.Checked:
            self.geomap = True
        else:
            self.geomap = False
        

    #set label for calendar clicks
    def showDate(self, date):
        self.ui.datelabel.setText(date.toString())

    #sets the table name to be used in search
    def getTableName(self):
        #enable search button, set table name and table name label
        self.ui.searchTextButton.setEnabled(True)
        self.table_name = str(self.ui.comboBox.currentText())
        self.ui.TableLabel.setText(str(self.ui.comboBox.currentText()))
        

        #query for grabbing column names in table
        query = "select column_name from information_schema.columns where table_name = '" + str(self.ui.comboBox.currentText()) + "'"
        cursor.execute(query)
        results = cursor.fetchall()
        

        #adds column names to list widget
        col_list = []
        for x in range(len(results)):
            col_list.append(results[x][0])
        
        self.ui.listWidgetColumns.clear()
        self.ui.listWidgetColumns.addItems(col_list)

    #main function for handling search terms
    def getSearchText(self):
        try:
            top_search_text = self.ui.top_search.text
        except Exception as e:
            print(e.args)
        #get all the info needed to perform search
        search_text = self.ui.searchTextInput.text()
        self.device_used = self.ui.device_used_combo.currentText()
        self.text_combo_box = self.ui.text_hashtag_combo.currentText()
        

        #builds query based on search terms
        if self.text_combo_box == 'text':
            if self.device_used == 'any device':
                query = "select distinct text from " + self.table_name + " where text like'%"+search_text+"%'"
            else:
                query = "select distinct text from " + self.table_name + " where text like'%"+search_text+"%' and source='"+self.device_used+"'"
        elif self.text_combo_box == 'hashtags':
            if self.device_used == 'any device':
                query = "select hashtags from " + self.table_name + " where text like '%"+search_text+"%'"
            else:
                query = "select hashtags from " + self.table_name + " where text like'%" + search_text + "%' and source='" + self.device_used + "'"

        elif self.text_combo_box == 'mentions':
            if self.device_used == 'any device':
                query = "select mentions from " + self.table_name + " where text like '%"+search_text+"%'"
            else:
                query = "select mentions from " + self.table_name + " where text like'%" + search_text + "%' and source='" + self.device_used + "'"
        
        try :
            cursor.execute(query)
            results = cursor.fetchall()
        except Exception:
            pass
        #if results not null
        if results:
            
            #if hashtag or mentions combobox selected
            if self.text_combo_box == 'hashtags' or self.text_combo_box == 'mentions' and results:
                hash_list = []
                hash_string = ''
                temp_list = []
                hash_dict = {}
                #for each line in results
                for x in range(len(results)):
                    hash_string = results[x][0]
                    #hashtags and mentions separated by '/', omit results with '?' because that is funky data
                    #if there is no '/' continue to next loop
                    if '/' in hash_string and '?' not in hash_string:
                        temp_list = hash_string.split('/')
                        for x in range(len(temp_list)):
                            hash_list.append(temp_list[x])
                #increment the amount of times we find a hashtag or mention
                for x in range(len(hash_list)):
                    if hash_list[x] not in hash_dict:
                        hash_dict[hash_list[x]] = 1
                    else:
                        hash_dict[hash_list[x]] += 1
                
                #delete blank entries
                if '' in hash_dict:
                    del hash_dict['']
            
            word_string = ""
            #append each result to word string followed be a period. This should probably be changed
            for x in range(len(results)):
                word_string += results[x][0] + "."
            blob = TextBlob(word_string)
            #sentiment analysis chart
            if self.sentiment_analysis:
                #popup graph
                matplotlib.use('Qt5Agg')
                
                sent_list = [0, 0, 0]
                sent_list_names = ['Positive', 'Neutral', 'Negative']
                for sentence in blob.sentences:
                    if sentence.polarity > 0:
                        sent_list[0] += 1
                    elif sentence.polarity == 0:
                        sent_list[1] += 1
                    else:
                        sent_list[2] += 1
                #zip lists to be used in pandas dataframe
                top_words = list(zip(sent_list_names, sent_list))

                df = pd.DataFrame(top_words, columns=['Sentiment Analysis', 'count'])

                axes = df.plot.bar(x='Sentiment Analysis', y='count', legend=False)
                plt.gcf().tight_layout()

                plt.show()
            #count words
            items = blob.word_counts.items()
            #omit stop words
            items = [item for item in items if item[0] not in self.stop_words]
            # equivalent code
            # items2 = []
            # for item in items:
            #   if item[0] not in stop_words:
            #       items2.append(item)

            #sort the items in descending order
            sorted_items = sorted(items, key=itemgetter(1), reverse=True)
            #limit top words to value of horizontal slider
            top_words = sorted_items[0:self.horizontal_slider_value]
            
            #if top words is not null
            if top_words:

                
                list1 = [''] * int(self.horizontal_slider_value)
                list2 = [0] * int(self.horizontal_slider_value)
                matplotlib.use('Qt5Agg')
                
                #if searching text
                if self.ui.text_hashtag_combo.currentText() == 'text':
                    #set the amount to the length of top words if it is less than the value of the slider
                    if len(top_words) < int(self.horizontal_slider_value):
                        for x in range(len(top_words)):
                            list1[x] = top_words[x][0]
                            list2[x] = top_words[x][1]
                    else:
                        for x in range(int(self.horizontal_slider_value)):
                            list1[x] = top_words[x][0]
                            list2[x] = top_words[x][1]
                        
                #if searching hashtags or mentions
                elif self.ui.text_hashtag_combo.currentText() == 'hashtags' or self.ui.text_hashtag_combo.currentText() == 'mentions':
                    name_list = []
                    count_list = []
                    
                    #append each key and value to each list
                    for key in hash_dict:
                        name_list.append(key)
                    for values in hash_dict.values():
                        count_list.append(values)
					#sort lists
                    for x in range(len(name_list)):
                        for y in range(len(name_list)):
                            if count_list[y] < count_list[x]:
                                placeholder = count_list[y]
                                count_list[y] = count_list[x]
                                count_list[x] = placeholder
                                
                                placeholder = name_list[y]
                                name_list[y] = name_list[x]
                                name_list[x] = placeholder
                    #reduce lists and zip them together - need to change
                    list1 = name_list[0:self.horizontal_slider_value]
                    list2 = count_list[0:self.horizontal_slider_value]
                    
                    top_words = list(zip(list1, list2))

                #if bar chart is selected
                if self.barchart:
                    word = ''
                    #check which combo box is selected and use that for the x axis name
                    if self.text_combo_box == 'mentions':
                        word = 'mentions'
                    if self.text_combo_box == 'hashtags':
                        word = 'hashtags'
                    if self.text_combo_box == 'text':
                        word = 'word'
                    
                    df = pd.DataFrame(top_words, columns=[word, 'count'])

                    axes = df.plot.bar(x=word, y='count', legend=False)
                    plt.gcf().tight_layout()
                    plt.show()
                #if geo map is selected
                if self.geomap:
                    
                    #initialize folium map
                    self.usmap = folium.Map(location=[39.8283, -98.5795],
                                            tiles='Stamen Terrain',
                                            zoom_start=5,
                                            detect_retina=True)
                    #query statements for bounding box of coordinates
                    querycoords0 = "select coordinates_00, id_string from user_locations where table_name='" + str(
                        self.ui.comboBox.currentText()) + "'"
                    querycoords1 = "select coordinates_01 from user_locations where table_name='" + str(
                        self.ui.comboBox.currentText()) + "'"
                    querycoords2 = "select coordinates_10 from user_locations where table_name='" + str(
                        self.ui.comboBox.currentText()) + "'"
                    querycoords3 = "select coordinates_11 from user_locations where table_name='" + str(
                        self.ui.comboBox.currentText()) + "'"
                    querycoords4 = "select coordinates_20 from user_locations where table_name='" + str(
                        self.ui.comboBox.currentText()) + "'"
                    querycoords5 = "select coordinates_21 from user_locations where table_name='" + str(
                        self.ui.comboBox.currentText()) + "'"
                    querycoords6 = "select coordinates_30 from user_locations where table_name='" + str(
                        self.ui.comboBox.currentText()) + "'"
                    querycoords7 = "select coordinates_31 from user_locations where table_name='" + str(
                        self.ui.comboBox.currentText()) + "'"
                    
                    cursor.execute(querycoords0)
                    resultcoords0 = cursor.fetchall()
                    cursor.execute(querycoords1)
                    resultcoords1 = cursor.fetchall()
                    cursor.execute(querycoords2)
                    resultcoords2 = cursor.fetchall()
                    cursor.execute(querycoords3)
                    resultcoords3 = cursor.fetchall()
                    cursor.execute(querycoords4)
                    resultcoords4 = cursor.fetchall()
                    cursor.execute(querycoords5)
                    resultcoords5 = cursor.fetchall()
                    cursor.execute(querycoords6)
                    resultcoords6 = cursor.fetchall()
                    cursor.execute(querycoords7)
                    resultcoords7 = cursor.fetchall()
                    

                    if resultcoords0:
                        text_query = "select text from " + self.table_name + " where place='" + resultcoords0[0][1] + "'"
                        
                        cursor.execute(text_query)
                        results = cursor.fetchall()
                        

                        if results:
                            
                            try:
                                x = 0
                                for row in resultcoords0:
                                    # get the text of the tweet that has geo info
                                    text_query = "select text from " + self.table_name + " where place='" + \
                                                 resultcoords0[x][1] + "'"
                                    cursor.execute(text_query)
                                    results = cursor.fetchall()

                                    # create popup marker
                                    popup = folium.Popup(results[0][0], parse_html='True')
                                    # create marker
                                    marker = folium.Marker((resultcoords1[x][0], resultcoords0[x][0]), popup=popup)
                                    # add marker to map
                                    marker.add_to(self.usmap)
                                    x += 1

                                x = 0
                                print('here 1')
                                # get the other coordinates and add markers to show boundary box
                                for row in resultcoords3:
                                    popup = folium.Popup('2', parse_html='True')
                                    marker = folium.Marker((resultcoords3[x][0], resultcoords2[x][0]), popup=popup)
                                    marker.add_to(self.usmap)
                                    x += 1

                                x = 0
                                print('here 2')
                                for row in resultcoords5:
                                    popup = folium.Popup('3', parse_html='True')
                                    marker = folium.Marker((resultcoords5[x][0], resultcoords4[x][0]), popup=popup)
                                    marker.add_to(self.usmap)
                                    x += 1

                                x = 0
                                print('here 3')
                                for row in resultcoords7:
                                    popup = folium.Popup('4', parse_html='True')
                                    marker = folium.Marker((resultcoords7[x][0], resultcoords6[x][0]), popup=popup)
                                    marker.add_to(self.usmap)
                                    x += 1
                                x = 0
                                # save map
                                self.usmap.save('tweet_map' + self.table_name + '.html')
                            except Exception:
                                pass


if __name__== "__main__":
    app = QApplication(sys.argv)
    w = MyForm()
    w.show()
    sys.exit(app.exec_())