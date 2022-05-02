# Function to simplify the expressions and query based on the format of the two
# Input should always be in the correct form only basic selects available, multiple quarries possible with AND
# CORRECT FORMAT: should always involve spaces between the different query inputs
# QGIS Query can differentiate between a String or a Double/ number, not necessary to leave ' ' for the numbers 
def get_query(query):
    finalquery= ""
    expression = query.split()
    helper=0
    for i in expression:
        if helper ==3 or i =='AND' :
            finalquery = finalquery + ' AND '
            helper =0
        elif helper ==0:
            attribute = i
            helper+=1
        elif helper ==1:
            expression = i
            helper+=1
        elif helper ==2:
            value = i
            finalquery = finalquery + "\"%s\"%s \'%s\'" % (attribute , expression ,value)
            helper+=1
    return finalquery
