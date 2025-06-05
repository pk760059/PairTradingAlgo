def scr_retrival(cname,dlist,date_format='%d-%m-%Y'):
    
    
    
    '''
    This function retrieves the data for scores from the merged and make sure the Data integrity is intact.
    It matched dates and all
    
    
    
    '''
    
    try:
        x2df=pd.read_csv(fr'C:\Users\acer\Desktop\Py-Fin\Fin_data\Fin_data\Data\Merged Scores\{cname}.csv')
        # x2df=pd.read_csv(f'Data\Merged Scores\{cname}.csv')
        # print(x2df)
        print("Ran till here")
        x2df['DateTime'] = pd.to_datetime(x2df['DateTime'], format=date_format)

        dlist = pd.to_datetime(dlist, format=date_format)
        
        dates_df = pd.DataFrame(dlist, columns=['DateTime'])

        # Merge the dates_df with x2df to ensure all dates from dlist are included
        filtered_df = pd.merge(dates_df, x2df, on='DateTime', how='left')
        filtered_df['DateTime'] = filtered_df['DateTime'].dt.strftime(date_format)
        # filtered_df = x2df[x2df['DateTime'].isin(dlist)]
        filtered_df=filtered_df.iloc[:,1:]
        return filtered_df

    except Exception as e: 
        print(f'Issue in finding {cname} merged file.\n Reason Being -> {e}')
        return None