import webui_api_package_query_combined
import sys

model_name = sys.argv[1]
ip = sys.argv[2]
port = sys.argv[3]

##### For a given model and dataset, this code will test the generated packages for hallucinations while implementing
##### Mitigation measures, namely a combination of RAG, fine-tuning, and self-detection.

##### This code currently requires the text-generation-webui tool
##### Need to input path to model and data!
data_path = ""
model_path = ""

########## Querying Package Data Sets

#Get package recommendations from the model
webui_api_package_query_combined.query_API(1,
                                  f"{model_path}/{model_name}/Package_LY_Master.json",
                                  f"{model_path}/{model_name}/Package_LY_packages_1.json", ip, port)
print("Package Data Set 1, Query 1 complete")
webui_api_package_query_combined.query_API(2,
                                  f"{data_path}/Package_LY.json",
                                  f"{model_path}/{model_name}/Package_LY_packages_2.json", ip, port)
print("Package Data Set 1, Query 2 complete")

webui_api_package_query_combined.query_API(1,
                                  f"{model_path}/{model_name}/Package_AT_Master.json",
                                  f"{model_path}/{model_name}/Package_AT_packages_1.json", ip, port)

print("Package Data Set 2, Query 1 complete")
webui_api_package_query_combined.query_API(2,
                                  f"{data_path}/Package_AT.json",
                                  f"{model_path}/{model_name}/Package_AT_packages_2.json", ip, port)
print("Package Data Set 2, Query 2 complete")

############## Querying Stack Overflow Data Sets
############## Stack Overflow - Data Set 1
webui_api_package_query_combined.query_API(1,
                                  f"{model_path}/{model_name}/SO_LY_Master.json",
                                  f"{model_path}/{model_name}/SO_LY_packages_1.json", ip, port)
print("Stack Overflow Data Set 1 - Query 1 complete")

webui_api_package_query_combined.query_API(2,
                                  f"{data_path}/SO_LY.json",
                                  f"{model_path}/{model_name}/SO_LY_packages_2.json", ip, port)
print("Stack Overflow Data Set 1 - Query 2 complete")

############## Stack Overflow - Data Set 2

webui_api_package_query_combined.query_API(1,
                                  f"{model_path}/{model_name}/SO_AT_Master.json",
                                  f"{model_path}/{model_name}/SO_AT_packages_1.json", ip, port)
print("Stack Overflow Data Set 2 - Query 1 complete")

webui_api_package_query_combined.query_API(2,
                                  f"{data_path}/SO_AT.json",
                                  f"{model_path}/{model_name}/SO_AT_packages_2.json", ip, port)
print("Stack Overflow Data Set 2 - Query 2 complete")

print("Tests complete")



