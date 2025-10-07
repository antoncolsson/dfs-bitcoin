from local_calls import convert_JsonToCsv, read_from_CSV, bitcoinDFS_search
import time
def main():
    print("Executing scripts...")
    # create a timer to measure the time it takes to execute the script
    start_time = time.time()
    
    #convert_JsonToCsv.convert_JSON_files_from_sub_folder("./data", "raw_transaction_metadata.csv") # denna används för att konvertera alla json filer i "/data" mappen till en csv fil, skapa en tom csv fil och byt filenamn i anrop
    #convert_JsonToCsv.convert_JSON_files_from_file_path("./data/1A1BLcXzZD4pLDPA5kYuBA11tAeatVjFha/full_info_1A1BLcXzZD4pLDPA5kYuBA11tAeatVjFha.json", "data3.csv")
    #read_from_CSV.highest_value_received("raw_transaction_metadata.csv")
   # data = read_from_CSV.check_if_address_exists_and_return_rows("raw_transaction_metadata.csv", "1A1BLcXzZD4pLDPA5kYuBA11tAeatVjFha")
    #data = read_from_CSV.check_address_folder("3BKGwmpn3cv2jgHRic96rNakozuRVGAGry")
    #for row in data:
    #print(data)
    #if testData is not None:
    bitcoinDFS_search.dfs_test("root")
    #tmp = read_from_CSV.get_nearest_send_transaction('./' + "testData/child_A/child_A.csv","child_A")
    #print(tmp)
    #print(read_from_CSV.get_largest_receiver(tmp))
   # print(len(data))
    print("Scripts executed successfully.")
    print("Execution time: %s seconds" % (time.time() - start_time))
if __name__ == "__main__":
    main()
# 111KvKxkeia8NeKMzqEDqnGm1v49Ncp3j