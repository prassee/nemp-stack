create table unnest_users 
ENGINE = IcebergS3('http://minio:9000/warehouse/unnest/users/', 'minioadmin', 'minioadmin') 
SETTINGS 
storage_catalog_type = 'rest' ,
storage_catalog_url = 'http://iceberg-rest:8181',
storage_warehouse = 'warehouse',
object_storage_endpoint = 'http://minio:9000',
storage_region = 'us-east-1';

create table unnest_events
ENGINE = IcebergS3('http://minio:9000/warehouse/unnest/events/', 'minioadmin', 'minioadmin') 
SETTINGS 
storage_catalog_type = 'rest' ,
storage_catalog_url = 'http://iceberg-rest:8181',
storage_warehouse = 'warehouse',
object_storage_endpoint = 'http://minio:9000',
storage_region = 'us-east-1';


select * from unnest_users as uu ;

select * from unnest_events as uu ;

